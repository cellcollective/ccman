# imports - standard imports
import os.path as osp
import subprocess
import gzip
import tempfile
import shutil
import logging

# imports - third-party imports
import dataset
import sqlalchemy

# imports - module imports
from   ccman.util.crypto   import generate_hash
from   ccman.system        import makedirs, popen, which, link, remove
from   ccman.bench.util    import _check_site
from   ccman.util.datetime import get_timestamp_str
from   ccman.environment   import getenv
import ccman

def get_db(name = "postgres", host = "127.0.0.1", port = 5432, username = "postgres", password = ""):
    prefix  = "POSTGRES"
    
    username = getenv("USER",     username, prefix = prefix)
    password = getenv("PASSWORD", password, prefix = prefix)

    name     = getenv("DB", name, prefix = prefix)

    connect_url = sqlalchemy.engine.url.URL(
        "postgres",
        username = username,
        password = password,
        host     = host,
        port     = port,
        database = name
    )
    connect_str = str(connect_url)

    db = dataset.connect(connect_str, engine_kwargs = dict(
        isolation_level = "AUTOCOMMIT"
    ))

    return db

class Site:
    def __init__(self, name, bench, check = True):
        self.name  = name
        self.bench = bench

        if check:
            ccman.log().info("Validating Site: {site}".format(site = self))
            _check_site(self.path, raise_err = True)

    @property
    def path(self):
        bench = self.bench
        name  = self.name

        path  = osp.join(bench.path, "sites", name)

        return path

    @property
    def cache(self):
        cache = ccman.Cache(location = self.path, dirname = ".site")
        return cache

    @property
    def config(self):
        cache  = self.cache
        cache.create()

        config = cache.get_config()

        return config

    def create(self, db_name = None, db_host = None, db_port = None, db_username = generate_hash(), db_password = generate_hash(), force = False):
        name    = self.name
        path    = self.path
        ccman.log().info("Creating Site Directory {path}".format(path = path))
        makedirs(path, exist_ok = force)

        source  = osp.join(self.bench.repo.working_dir, "cc", "public")
        target  = osp.join(self.path, "public")

        link(source, target, exist_ok = force)

        cache   = self.cache
        cache.create()

        db_name = db_name or generate_hash(name)
        
        # Since postgres doesn't accept names that start numerically.
        def _sanitize(string):
            return "_%s" % string if string[0].isdigit() else string
        
        db_name     = _sanitize(db_name)
        db_username = _sanitize(db_username)
        db_password = _sanitize(db_password)

        bench   = self.bench
        db_host = db_host or bench.get_config("database_host", ccman.const.host.db)
        db_port = db_port or bench.get_config("database_port", ccman.const.port.db)

        db      = get_db(host = db_host, port = db_port)

        def createdb():
            ccman.log().info("Creating DataBase {database}".format(
                database = db_name
            ))
            db.query("CREATE DATABASE %s" % db_name)

        try:
            createdb()
        except Exception as e:
            ccman.log().error("Failed to Create DataBase {database}".format(
                database = db_name
            ))
            ccman.log().error(e)

            if force:
                ccman.log().info("Dropping DataBase {database}".format(
                    database = db_name
                ))

                db.query("DROP DATABASE %s" % db_name)
                createdb()

        result = db.query("CREATE USER %s" % (db_username))
        query  = 'ALTER USER \"{username}\" WITH ENCRYPTED PASSWORD \'{password}\'; GRANT ALL PRIVILEGES ON DATABASE \"{database}\" TO \"{username}\"'.format(
            database = db_name,
            username = db_username,
            password = db_password,
        )
        db.query(query)

        self.set_config("database_name", db_name)
        self.set_config("database_host", db_host)
        self.set_config("database_port", db_port)
        self.set_config("database_username", db_username)
        self.set_config("database_password", db_password)

    def set_config(self, key, value):
        cache = self.cache
        cache.create()

        cache.set_config(key, value)

    def init(self):
        bench = self.bench
        cache = self.cache

        ccman.setenv("DATABASE_NAME",     cache.get_config("database_name"))
        ccman.setenv("DATABASE_HOST",     cache.get_config("database_host", bench.get_config("database_host", ccman.const.host.db)))
        ccman.setenv("DATABASE_PORT",     cache.get_config("database_port", bench.get_config("database_port", ccman.const.port.db)))
        ccman.setenv("DATABASE_USERNAME", cache.get_config("database_username"))
        ccman.setenv("DATABASE_PASSWORD", cache.get_config("database_password"))

    def backup(self, compress = True):
        timestamp = get_timestamp_str("%Y%m%d_%H%M%S")
        path      = osp.join(self.path, "backups", timestamp)
        makedirs(path)
            
        path_db   = osp.join(path, "{timestamp}.sql".format(timestamp = timestamp))
        ccman.log().info("Backing up DataBase for site {site} at {path}".format(
            site  = self,
            path  = path_db
        ))
        self._backup_database(fp = path_db, compress = gzip)

    def _backup_database(self, fp, compress = True):
        bench  = self.bench
        config = self.config

        env   = dict(
            PGHOST = config.get("database_host", bench.get_config("database_host", ccman.const.host.db)),
            PGPORT = config.get("database_port", bench.get_config("database_port", ccman.const.port.db))
        )
        
        popen("{pg_dump} {database} {gzip} > {path}".format(
            pg_dump  = which("pg_dump", raise_err = True),
            database = config.get("database_name"),
            gzip     = "| gzip" if compress else "",
            path     = osp.join("{path}.gz".format(path = fp)) if compress else fp
        ), env = env)

        ccman.log().info("Backing up {site} successful.".format(site = self))

    def restore(self, dbfile, static = None, force = False, raise_err = True):
        dbfile = osp.realpath(dbfile)
        
        if not osp.exists(dbfile):
            raise ccman.ValueError("{path} does not exists.".format(path = dbfile))
        
        fname, ext = osp.splitext(dbfile)
        tempdir    = None
        if ext in [".gz", ".gzip"]:
            tempdir = tempfile.mkdtemp()

            fname   = osp.basename(fname)
            fpath   = osp.join(tempdir, fname)
            
            with gzip.open(dbfile, "rb") as fin:
                with open(fpath, "wb") as fout:
                    shutil.copyfileobj(fin, fout)
                    dbfile = fpath

        bench  = self.bench
        config = self.config

        env   = dict(
            PGHOST     = config.get("database_host", bench.get_config("database_host", ccman.const.host.db)),
            PGPORT     = config.get("database_port", bench.get_config("database_port", ccman.const.port.db)),
            PGPASSWORD = config.get("database_password", bench.get_config("database_password")),
        )

        try:
            popen("{pg_restore}     \
                -U {db_user}        \
                -d {database}       \
                --no-owner          \
                --role {db_user}    \
                -v {dbfile}".format(
                pg_restore  = which("pg_restore", raise_err = True),
                database    = config.get("database_name"),
                db_user     = config.get("database_username"),
                dbfile      = dbfile
            ), env = env)
        except ccman.PopenError:
            if raise_err:
                raise

        if tempdir:
            shutil.rmtree(tempdir)

        if static:
            ccman.log().info("Restoring static files for site {site}.".format(site = self))
            
            fname, ext = osp.splitext(static)
            tempdir    = None
            if ext in [".gz", ".gzip"]:
                tempdir = tempfile.mkdtemp()

                fname   = osp.basename(fname)
                fpath   = osp.join(tempdir, fname)
                
                with gzip.open(static, "rb") as fin:
                    with open(fpath, "wb") as fout:
                        shutil.copyfileobj(fin, fout)
                        static = fpath

            bench  = self.bench
            dest   = osp.join(bench.path, "app")
            shutil.copytree(static, dest)

            if tempdir:
                shutil.rmtree(tempdir)
        
        ccman.log().info("Restoring site {site} successful.".format(site = self))

    def __repr__(self):
        return "<Site {name}>".format(
            name = self.name
        )

    def __eq__(self, other):
        return self.path == other.path