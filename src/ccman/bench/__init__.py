# imports - compatibility imports
import six

# imports - standard imports
import sys
import os
import os.path as osp
import re
import time
import shutil
import subprocess
from   subprocess import list2cmdline
from   datetime   import datetime
import getpass
import collections
import signal

# imports - third-party imports
import requests as req
import git
import gitlab
from   honcho.manager import Manager, Printer
import requests as req
import redis
import psycopg2

# imports - module imports
from   ccman.bench.site    import Site, get_db
from   ccman.bench.util    import (_get_yarn, _get_nginx_path, _check_bench, _BENCH_TREE, _get_available_port,
    _get_systemd_path, get_redis_connection)
from   ccman.system        import read, write, which, popen, makedirs, maketree, pardir, remove
from   ccman.util.crypto   import generate_hash
from   ccman.util.string   import strip
from   ccman.util.types    import sequencify, merge_dict, list_filter, dict_deep_update
from   ccman.util.imports  import import_handler
from   ccman.util          import json as _json
from   ccman.db            import connect as db_connect
from   ccman.environment   import getenv
from   ccman.commands.util import split_cmd_variables
import ccman

class Bench:
    def __init__(self, name, check = False, search_parent_directories = False):
        path  = osp.realpath(name)

        check = check or search_parent_directories

        if check:
            ccman.log().info("Validating Bench.".format(path = path))
            path = _check_bench(path, raise_err = check,
                search_parent_directories = search_parent_directories)
            # Patch
            ccman._bench = self

        self.path    = path
        
        # Patch - Don't refresh Logger Instance
        if ccman._bench:
            # ccman.log(refresh = True)
            pass

    @property
    def name(self):
        name = osp.basename(self.path)
        return name

    @property
    def mode(self):
        mode = ccman.getenv("ENVIRONMENT", "development")
        return mode

    @mode.setter
    def mode(self, value):
        ccman.setenv("ENVIRONMENT", value)

    @property
    def cache(self):
        cache = ccman.Cache(location = self.path,
            dirname = ".{name}".format(name = self.name))
        return cache

    @property
    def db(self):
        cache = self.cache
        cache.create()

        db    = db_connect("sqlite:///{location}/db.db".format(
            location = cache.path
        ), bootstrap = True)

        return db

    @property
    def version(self):
        try:
            path     = osp.join(self.repo.working_dir, "VERSION.txt")
            version  = read(path)
        except Exception:
            # reading version from package.json CC Version 2.2.8 onwards.
            path     = osp.join(self.repo.working_dir, "package.json")
            data     = _json.read(path)
            version  = data.version

        version = strip(version)

        return version

    @version.setter
    def version(self, value):
        path = self.repo.working_dir
        
        _json.update(osp.join(path, "package.json"), dict(version = value))
        
        repo = git.Repo(path)
        g    = repo.git
        g.add("package.json")

        g.commit("-m", "Bumped to version {version}".format(
            version = value
        ))

    @property
    def repo(self):
        path    = osp.join(self.path, "cellcollective")

        repo    = git.Repo(path)

        return repo

    @property
    def host(self):
        host       = ccman.Dict()

        host.web   = ccman.getenv("WEB_HOST",      self.get_config("web_host",      ccman.const.host.web))
        host.app   = ccman.getenv("APP_HOST",      self.get_config("app_host",      ccman.const.host.app))
        host.db    = ccman.getenv("DATABASE_HOST", self.get_config("database_host", ccman.const.host.db))
        host.cache = ccman.getenv("CACHE_HOST",    self.get_config("cache_host",    ccman.const.host.cache))

        return host

    @host.setter
    def host(self, value):
        if "web"   in value:
            self.set_config("web_host", value.web)
            ccman.setenv("WEB_HOST",    value.web)

        if "app"   in value:
            self.set_config("app_host", value.app)
            ccman.setenv("APP_HOST",    value.app)

        if "db"    in value:
            self.set_config("database_host", value.db)
            ccman.setenv("DATABASE_HOST",    value.db)

        if "cache" in value:
            self.set_config("cache_host", value.cache)
            ccman.setenv("CACHE_HOST",    value.cache)

    @property
    def port(self):
        port       = ccman.Dict()

        port.web   = ccman.getenv("WEB_PORT",      self.get_config("web_port",      ccman.const.port.web))
        port.app   = ccman.getenv("APP_HOST",      self.get_config("app_port",      ccman.const.port.app))
        port.db    = ccman.getenv("DATABASE_PORT", self.get_config("database_port", ccman.const.port.db))
        port.cache = ccman.getenv("CACHE_PORT",    self.get_config("cache_port",    ccman.const.port.cache))

        return port

    @port.setter
    def port(self, value):
        if "web"   in value:
            self.set_config("web_port",  value.web)
            ccman.setenv("WEB_PORT",     value.web)

        if "app"   in value:
            self.set_config("app_port",  value.app)
            ccman.setenv("APP_PORT",     value.app)

        if "db"    in value:
            self.set_config("database_port", value.db)
            ccman.setenv("DATABASE_PORT",    value.db)

        if "cache" in value:
            self.set_config("cache_port", value.cache)
            ccman.setenv("CACHE_HOST",    value.cache)

    @property
    def site(self):
        cache = self.cache

        name  = cache.get_config("default_site")
        site  = None
        
        if not name:
            sites = self.sites
            if len(sites) == 1:
                self.site = sites[0]
                site      = self.site
            else:
                raise ccman.ValueError("No site found in Bench {bench}.".format(
                    bench = self
                ))
        else:
            site = Site(name, self, check = True)

        return site

    @site.setter
    def site(self, value):
        cache = self.cache

        if isinstance(value, Site):
            value = value.name
            
        cache.set_config("default_site", value)

    @property
    def sites(self):
        path  = osp.join(self.path, "sites")
        sites = [Site(f, self) for f in os.listdir(path) if osp.isdir(path)]

        return sites

    @property
    def config(self):
        cache  = self.cache
        config = cache.get_config()

        return config

    def create(self,
        protocol     = "https",
        branch       = "develop",
        python       = sys.executable,
        web_host     = ccman.const.host.web,
        web_port     = ccman.const.port.web,
        app_host     = ccman.const.host.app,
        app_port     = ccman.const.port.app,
        db_host      = ccman.const.host.db,
        db_port      = ccman.const.port.db,
        cache_host   = ccman.const.host.cache,
        cache_port   = ccman.const.port.cache,
        site         = "foo.bar",
        force        = False,
        mode         = "development"
    ):
        ccman.log().info("Creating Bench at {path}".format(path = self.path))
        makedirs(self.path, exist_ok = force)

        protocol, seperator = ("https://", "/")          if protocol == "https" else ("git@", ":")

        URL   = "{protocol}{hostname}{seperator}{username}/{project}.git"
        
        ccman.log().info("Creating a Virtual Environment for ccman")
        ccenv = osp.join(self.path, ".ccenv")
        popen("{virtualenv} {name} --python {python}".format(
            virtualenv = which("virtualenv", raise_err = True),
            name       = ccenv,
            python     = which(python, raise_err = True)
        ), cwd = self.path)

        path = osp.join(self.path, ".ccman")

        if osp.exists(path):
            remove(path, recursive = True)

        url  = URL.format(
            protocol    = protocol,
            hostname    = "github.com",
            seperator   = seperator,
            username    = "helikarlab",
            project     = "ccman"
        )

        ccman.log().info("Using URL {url} to fetch Cell Collective Manager".format(url = url))
        repo = git.Repo.clone_from(url, path)

        ccman.log().info("Installing ccman")
        popen("{pip} install -e {ccman}".format(
            pip   = osp.join(".ccenv", "Scripts" if os.name == "nt" else "bin", "pip"),
            ccman = repo.working_dir
        ), cwd = self.path)
        
        path = osp.join(self.path, "cellcollective")

        if osp.exists(path):
            remove(path, recursive = True)

        url  = URL.format(
            protocol    = protocol,
            hostname    = "github.com",
            seperator   = seperator,
            username    = "helikarlab",
            project     = "cellcollective"
        )
        ccman.log().info("Using URL {url} to fetch Cell Collective".format(url = url))
    
        repo = git.Repo.clone_from(url, path)
        
        ccman.log().info("Checking out from branch {branch}".format(branch = branch))
        self.workon(branch, track = branch, stash = False, install = False)

        ccman.log().info("Creating Bench Directories")
        maketree(_BENCH_TREE, self.path, exist_ok = force)

        cache      = self.cache
        cache.create()

        web_port   = _get_available_port(web_port, host = web_host)
        app_port   = _get_available_port(app_port, host = app_host)
        
        self.host  = ccman.Dict({ "web": web_host, "app": app_host, "db": db_host, "cache": cache_host })
        self.port  = ccman.Dict({ "web": web_port, "app": app_port, "db": db_port, "cache": cache_port })

        if site:
            ccman.log().info("Creating a Default Site {site}".format(site = site))
            self.create_site(site,
                db_host = self.host.db,
                db_port = self.port.db,
                force   = force
            )

        self.build()

        self.register()

    def register(self, remove = False):
        benches = ccman.get_config("benches", [ ])
        
        if self.path not in benches:
            if remove:
                ccman.log().warning("Bench {bench} already removed.".format(bench = self))
            else:
                benches.append(self.path)
                ccman.cache.set_config("benches", benches)
                ccman.log().info("Successfully registered Bench {bench}".format(bench = self))
        else:
            if remove:
                benches.remove(self.path)
                ccman.cache.set_config("benches", benches)
                ccman.log().info("Successfully removed Bench {bench}".format(bench = self))
            else:
                ccman.log().warning("Bench {bench} already registered.".format(bench = self))

    def workon(self, branch, remote = "upstream", track = "develop", tag = None, stash = True, install = True):
        repo   = self.repo
        ccman.log().info("Fetching Latest from remote {remote}".format(remote = remote))
        remote = repo.remotes[remote]
        
        if repo.git.status("-s"):
            if stash:
                ccman.log().info("Stashing Uncommitted and Untracked files")
                repo.git.stash("--include-untracked")

        if branch in ("develop", "master", "hotfix"):
            track = branch

        ccman.log().info("Checking out from Branch {branch} tracking {remote}/{track}".format(
            branch = branch,
            remote = remote,
            track  = track
        ))

        if not tag:
            remote.fetch()

            args = list_filter([
                "-f" if not stash else "",
                "-B", branch,
                "--track", "{remote}/{branch}".format(
                    remote = remote,
                    branch = track
                )
            ], bool)
            repo.git.checkout(*args)
        else:
            remote.fetch("--tags")

            if not branch.startswith("v"):
                branch = "v{tag}".format(tag = branch)

            args   = list_filter([
                "-f" if not stash else "",
                "tags/{tag}".format(tag = branch),
                "-B", branch,
            ], bool)
            repo.git.checkout(*args)

        if stash and repo.git.stash("list"):
            ccman.log().info("Applying Stash")
            repo.git.stash("apply")
        else:
            if repo.git.status("-s"):
                ccman.log().info("Removing Untracked Files/Directories.")
                repo.git.clean("-d", "-f")
        
        if install:
            self.install(pure = not stash)

    def install(self, pure = False):
        yarn   = _get_yarn()

        repo   = self.repo
        ccman.log().info("Installing Dependencies using {yarn}".format(yarn = yarn))
        popen("{yarn} install {pure}".format(
            yarn = yarn,
            pure = "--pure-lockfile" if pure else ""
        ), cwd = repo.working_dir)

    def build(self, mode = "development", variables = { }, watch = False, install = True, ignore = [ ],
        locales = False
    ):
        variables = self._get_variables(variables = variables)

        if install:
            self.install()

        path      = self.path
        
        yarn      = _get_yarn()
        
        path      = self.repo.working_dir

        self._build_info(mode = mode, variables = variables)

        # Backward Compatibility
        if "app" not in ignore and self.sites:
            self._build_ccappserver()

        if watch:
            ccman.log().info("Watching Bench")
        else:
            ccman.log().info("Building Bench")

        self.mode = mode

        if locales:
            popen("%s run build"       % yarn, cwd = path)
            popen("%s run build:langs" % yarn, cwd = path)

        popen("{yarn} run {command}".format(
            yarn    = yarn,
            command = "start" if watch else "build"
        ), cwd = path)

    def _build_info(self, mode = "development", variables = { }):
        # api = ccman.const.DEPRECATED.url[mode]
        if mode == "production":
            api = ccman.const.DEPRECATED.url[mode]
        else:
            api = "http://%s:%s/" % (self.host.app, self.port.app)
            
        ccman.setenv("DEPRECATED_API_URL", api)
        
        ccman.log().info("Creating Build Info")
        context = \
        {
               "date": datetime.now(),
              "bench": self,
                "api": api,
               "mode": mode,
               "urls": \
                {
                    " base": "http://%s:%s/" % (self.host.web, self.port.web),
                    "learn": "http://%s:%s/" % (self.host.web, self.port.web),
                    "teach": "http://%s:%s/" % (self.host.web, self.port.web)
                }
        }
        context  = dict_deep_update(context, variables)

        path     = self.repo.working_dir
        template = ccman.render_template("app.json", context)

        back     = False

        if osp.exists(osp.join(path, "ccfrontend")):
            # BC
            back = True
            dest = osp.join(path, "ccfrontend", "app", "app.json")
        else:
            dest = osp.join(path, "cc", "client", "app", "app.json")

        write(dest, template, force = True)

        if not back:
            self._build_app_manifest()

        if self.sites:
            self._build_sequelize_config()

    def _build_app_manifest(self):
        path     = self.repo.working_dir

        source   = osp.join(path, "cc", "client", "app", "app.json")
        config   = _json.read(source)

        template = ccman.render_template("manifest.json", dict(app = config))

        dest     = osp.join(path, "cc", "public", "manifest.json")

        write(dest, template, force = True)

    def _build_sequelize_config(self):
        ccman.log().info("Building Sequelize Configuration")

        context  = dict(bench = self)
        template = ccman.render_template("sequelize.config.json", context = context)
        self.add_config(osp.join("sequelize", "config.json"), template, force = True)

    def _build_nginx_configs(self, force = False):
        ccman.log().info("Building NGINX Configuration")

        if sys.platform.startswith("linux"):
            context  = dict(bench = self)
            template = ccman.render_template(osp.join("config", "nginx.conf"), context = context)
            
            path     = osp.join(_get_nginx_path(), "sites-available", self.site.name)

            write(path, template, force = force)

    def _build_systemd_config(self, force = False):
        ccman.log().info("Building systemd Configuration")

        if sys.platform.startswith("linux"):
            user     = getpass.getuser()
            context  = dict(bench = self, user = user)
            template = ccman.render_template(osp.join("config", "systemd", "bench.service"), context = context)

            path     = osp.join(_get_systemd_path(), "{name}.service".format(name = self.name))

            # write(path, template, force = force)

    def _build_ccappserver(self):
        ccapp   = osp.join(self.repo.working_dir,"ccappserver")

        path    = osp.join(ccapp,"cc.application")
        gradle  = which("gradle", raise_err = True) 
        popen(gradle, "build", cwd = path)

        # move jar to app/bin
        version = "2.1.6"
        jar     = "cc-application-server-%s.jar" % version

        base_source  = osp.join(ccapp,
            "cc.application","cc.application.main",
            "build","libs"
        ) 
        app     = osp.join(self.path,"app")
        dest    = osp.join(app, "bin")
        makedirs(dest, exist_ok = True)
        
        if osp.exists(osp.join(base_source, "app.jar")):
            source = osp.join(base_source, "app.jar")
        else:
            source = osp.join(base_source, jar)

        shutil.copy2(source, osp.join(dest, jar))

        # make conf
        conf     = osp.join(app, "conf")
        makedirs(conf, exist_ok = True)
        
        fname    = "jdbc.properties"
        template = ccman.render_template(fname, dict(bench = self))

        write(osp.join(conf, fname), template, force = True)

        def _copy_conf(name):
            source   = osp.join(ccapp,
                "cc.application","deploy.server",
                "app","conf"
            )
            shutil.copy2(osp.join(source, name), osp.join(conf, name))

        _copy_conf("server-logback.xml")
        _copy_conf("simulation-config.xml")

    def init(self):
        ccman.setenv("BENCH_PATH", self.path)
        
        ccman.setenv("WEB_HOST", self.host.web)
        ccman.setenv("WEB_PORT", self.port.web)

        ccman.setenv("APP_HOST", self.host.app)
        ccman.setenv("APP_PORT", self.port.app)

        ccman.setenv("CACHE_HOST", self.host.cache)
        ccman.setenv("CACHE_PORT", self.port.cache)

        # For Sequelize.
        ccman.setenv("PGHOST", self.host.db, prefix = False)
        ccman.setenv("PGPORT", self.port.db, prefix = False)
        
        ccman.setenv("DATABASE_HOST", self.host.db)
        ccman.setenv("DATABASE_PORT", self.port.db)

        mode = self.mode

        if mode == "production":
            api = ccman.const.DEPRECATED.url[mode]
        else:
            api = "http://%s:%s/" % (self.host.app, self.port.app)

        if not ccman.getenv("DEPRECATED_API_URL"):
            ccman.setenv("DEPRECATED_API_URL", api)

        self.site.init()

    def _get_variables(self, variables = { }):
        if variables and not isinstance(variables, collections.Mapping):
            if osp.exists(variables):
                variables = _json.read(variables)
            else:
                variables = split_cmd_variables(variables)

        return variables

    def start(self,
        mode       = "development",
        install    = True,
        build      = True,
        variables  = dict(),
        ignore     = [ ],
        quiet      = [ ]
    ):
        self.mode  = mode

        variables  = self._get_variables(variables = variables)

        if install:
            self.install()

        if build:
            self.build(install = False, mode = mode, variables = variables,
                ignore = ignore
            )

        web_host  = self.host.web
        web_port  = self.port.web

        app_host  = self.host.app
        app_port  = self.port.app

        self.init()
        self.site.init()

        ccman_    = osp.join(self.path, ".ccenv", "bin", "ccman")
        daemons   = list_filter([
            ccman.Dict({
                    "name": "web",
                "command": [ccman_, "run", "web",
                    "--host", web_host, "--port", web_port
                ]
            }),
            ccman.Dict({
                   "name": "app",
                "command": [ccman_, "run", "app",
                    "--host", app_host, "--port", app_port
                ]
            })
        ], lambda x: x.name not in ignore)

        docker    = getenv("DOCKER", False)

        if mode == "development" and not docker:
            path     = osp.join(self.path, "logs", "process.log")
            printers = [
                Printer(),
                Printer(output = open(path, "a"))
            ]
            manager  = Manager(printer = printers)

            for daemon in daemons:
                name = "{bench} {name}".format(
                    bench = self,
                    name  = daemon.name
                )
                command = list2cmdline([str(arg) for arg in daemon.command])
                manager.add_process(
                    name,
                    command,
                    quiet = daemon.name in quiet, 
                    cwd   = self.path,
                    env   = dict(CC_ENVIRONMENT = self.mode)
                )

            ccman.log().info("Launching Processes in {mode} mode.".format(mode = mode))

            manager.loop()
            code = manager.returncode

            return code
        else:
            self.run("web", host = web_host, port = web_port, mode = mode)
            self.run("app", host = app_host, port = app_port, mode = mode)

    def run(self, type_, *args, **kwargs):
        self.mode = kwargs.get("mode", "development")

        docker    = getenv("DOCKER", False)

        if   type_ == "web":
            host = kwargs.get("host", ccman.const.host.web)
            port = kwargs.get("port", ccman.const.port.web)

            self.host = ccman.Dict({ "web": host })
            self.port = ccman.Dict({ "web": port })

            self.init()
            self.site.init()

            try:
                command = "{yarn} run {command}".format(
                    yarn    = _get_yarn(),
                    command = "start:{mode}".format(mode = "docker" if docker else self.mode)
                )
                popen(command, cwd = self.repo.working_dir)
            except ccman.PopenError:
                # BC
                command = "{yarn} run {command}".format(
                    yarn    = _get_yarn(),
                    command = "start"
                )
                popen(command, cwd = self.repo.working_dir)
        elif type_ == "test":
            self.init()
            self.site.init()

            self._run_test()
        elif type_ == "app":
            app       = osp.join(self.path, "app")

            version   = "2.1.6"
            jar       = osp.join(app,"bin","cc-application-server-%s.jar" % version)

            host      = kwargs.get("host", ccman.const.host.app)
            port      = kwargs.get("port", ccman.const.port.app)

            self.host = ccman.Dict({ "app": host })
            self.port = ccman.Dict({ "app": port })

            self.init()
            self.site.init()

            java      = which("java", raise_err = True)
            profiles  = dict(
                development = "local",
                test        = "test",
                production  = "prod"
            )
            args      = [
                "-jar",             jar,
                "--server-port",    port,
                "--logging.config", osp.join(app, "conf", "server-logback.xml"),
                "--spring.profiles.active", profiles[self.mode]
            ]

            env       = merge_dict(self._get_pg_envvars(), dict(CC_ROOT_DIR = app))
                
            if self.mode == "production":
                args = args + [
                    " >> ",
                    osp.join(self.path, "logs", "app.log") 
                ]

                dirpid  = osp.join(self.path, "pids")
                makedirs(dirpid, exist_ok = True)

                path    = osp.join(dirpid, "app.pid")
                
                if os.path.exists(path):
                    ccman.log().info("App Service already running. Shutting down...")
                    pid = int(read(path))
                    os.kill(pid, signal.SIGTERM)
                    ccman.log().info("Successfully shutdown app service.")
                    remove(path)

                proc = popen(java, *args, env = env, wait = False)
                write(path, str(proc.pid))
            else:
                popen(java, *args, env = env)
        else:
            raise ccman.ValueError("Unknown process type {type_}".format(
                type_ = type_
            ))

    def _run_test(self):
        gitlab_runner = which("gitlab-runner", raise_err = True)
        popen("sudo {gitlab_runner} exec docker test".format(
            gitlab_runner = gitlab_runner
        ), cwd = self.repo.working_dir)

    def stop(self):
        ccman.log().info("Shutting down Web...")
        popen("npx pm2 stop cc", pwd = self.repo.working_dir)

        ccman.log().info("Shutting down App...")
        path = osp.join(self.path, "pids", "app.pid")
        if os.path.exists(path):
            ccman.log().info("App Service already running. Shutting down...")
            pid = int(read(path))
            os.kill(pid, signal.SIGTERM)
            ccman.log().info("Successfully shutdown app service.")
            remove(path)
        else:
            ccman.log().info("App already shutdown.")

    def patch(self):
        with open(ccman.path.patches) as patches:
            regex = r"v[0-9]*_?[0-9]*_?[0-9]*"

            for patch in patches:
                patch   = strip(patch)
                version = re.search(regex, patch).group()

                version = version.strip("v").replace("_", ".")

                if version in ccman.__version__:
                    executed = self.db.query("SELECT * FROM tabPatch")
                    names    = [e["name"] for e in executed]
                    
                    if patch not in names:
                        patch    = strip(patch)
                        runner   = import_handler(patch)

                        ccman.log().info("Running Patch {patch}".format(patch = patch))
                        
                        start    = time.time()
                        runner.run(bench = self)
                        end      = time.time()

                        duration = end - start

                        self.db.query("INSERT INTO tabPatch (name, duration) VALUES ('{}', {})".format(patch, duration))

    def update(self, ccman_only = False, mode = "development", remote = "upstream", branch = "develop", clean = True, patch = True,
        build = True, install = True, reset = True, variables= { }):
        variables = self._get_variables(variables)
        
        ccman.log().info("Updating ccman")

        path  = osp.join(self.path, ".ccman")
        repo  = git.Repo(path)
        repo.git.pull()

        ccman.log().info("Installing ccman")
        popen("{pip} install -e {ccman}".format(
            pip   = osp.join(self.path, ".ccenv", "Scripts" if os.name == "nt" else "bin", "pip"),
            ccman = path
        ))

        if not ccman_only:
            repo = self.repo
            repo.git.fetch("--tags")

            self.workon(branch, track = branch, remote = remote, stash = not reset, install = False)

            if clean:
                self.clean()

            if patch:
                self.patch()

            if build:
                self.build(mode = mode, install = install, variables = variables)

    def clean(self, force = False, destroy = False):
        yarn = _get_yarn()
        cwd  = osp.join(self.repo.working_dir)
        
        ccman.log().info("Cleaning Build")
        popen("{yarn} run clean".format(
            yarn = yarn
        ), cwd = cwd, raise_err = False) # Backward Compat
        
        if force:
            # Remove everything mentioned within .gitignore
            popen("git clean -dfX", cwd = self.repo.working_dir)

            # node_modules = osp.join(self.repo.working_dir, "node_modules")
            # ccman.log().info("Cleaning node_modules - {path}".format(path = node_modules))
            # remove(node_modules, recursive = True, raise_err = False)

            ccman.log().info("Cleaning yarn cache")
            popen("{yarn} cache clean".format(yarn = yarn))

            ccman.log().info("Cleaning Redis Cache")
            redis = get_redis_connection(host = self.host.cache, port = self.port.cache, refresh = True, raise_err = False)
            if redis:
                redis.flushall()
            else:
                ccman.log().warn("Unable to connect to Redis Cache.")

            if destroy:
                ccman.log().info("Cleaning pm2 cache")
                popen("rm -rf ~/.pm2")

    def backup(self, sites = [ ], compress = True, raise_err = True):
        sites = sequencify(sites)

        if not sites:
            for site in self.sites:
                site.backup(compress = compress)
        else:
            for site in sites:
                site = Site(site, self, check = raise_err)

                if not site in self.sites and raise_err:
                    raise ccman.ValueError("No site named {site}.".format(site = site))
                else:
                    site.backup(compress = compress)

    def restore(self, sites, dbfile, static = None, raise_err = True, force = False):
        dbfile = osp.realpath(dbfile)
        sites  = sequencify(sites)

        ccman.log().info("Restoring {dbfile} into {sites}".format(dbfile = dbfile, sites = sites))

        for site in sites:
            site = Site(site, self, check = raise_err)

            if not site in self.sites and raise_err:
                raise ccman.ValueError("No site named {site}.".format(site = site))
            else:
                site.restore(dbfile, static = static, raise_err = raise_err, force = force)

    def test(self, install = False, build = False, coverage = True):
        ccman.log().info("Testing Bench.")

        if install:
            self.install()

        if build:
            self.build(install = False)

        self.mode = "test"

        yarn = _get_yarn()
        path = self.repo.working_dir

        self.init()
        self.site.init()
        
        popen("{yarn} test".format(
            yarn = yarn
        ), cwd = path)

    def get_config(self, key = None, default = None, check = False, crypt = False):
        if self.cache.exists():
            value = self.cache.get_config(key = key, default = default, check = check, crypt = crypt)
        else:
            key   = ccman.config.check_key(key, raise_err = check)
            value = default
        
        return value

    def set_config(self, key, value, crypt = False):
        self.cache.create()
        self.cache.set_config(key, value, crypt = crypt)
    
    def add_config(self, fname, config, force = False):
        path = osp.join(self.path, "configs", fname)
        dirs = osp.dirname(path)
        makedirs(dirs, exist_ok = force)
        
        write(path, config, force = force)

    def create_site(self, name,
        db_name     = None,
        db_host     = None,
        db_port     = None,
        db_username = generate_hash(),
        db_password = generate_hash(),
        force       = False,
        default     = False,
    ):
        site = Site(name, self, check = False)
        site.create(
            db_name     = db_name,
            db_host     = db_host,
            db_port     = db_port,
            db_username = db_username,
            db_password = db_password,
            force       = force
        )

        if default:
            self.site = site

        return site

    def setup(self, type_, *args, **kwargs):
        if type_ == "ssl":
            sites     = kwargs.get("sites") or self.sites
            raise_err = kwargs.get("raise_err", True)
            self._setup_ssl(sites = sites, raise_err = raise_err)

    def _setup_ssl(self, sites = [ ], raise_err = True):
        sites = sites or self.sites
        for site in sites:
            site = Site(site, self, check = raise_err)

        raise ccman.NotImplementedError()

    def status(self, web = True, app = True, db = True, cache = True, verbose = False):
        status     = ccman.Dict()

        if web:
            status_web = self._check_web_status()
            if verbose:
                status.web.host   = self.host.web
                status.web.port   = self.port.web
                status.web.status = status_web
            else:
                status.web        = status_web
        if app:
            status_app = self._check_app_status()
            if verbose:
                status.app.host   = self.host.app
                status.app.port   = self.port.app
                status.app.status = status_app
            else:
                status.app        = status_app    
        if db:
            status_db  = self._check_db_status()
            if verbose:
                status.db.host   = self.host.db
                status.db.port   = self.port.db
                status.db.status = status_db
            else:
                status.db        = status_db
        if cache:
            status_cache = self._check_cache_status()
            if verbose:
                status.cache.host   = self.host.cache
                status.cache.port   = self.port.cache
                status.cache.status = status_cache
            else: 
                status.cache        = status_cache

        return status

    def _check_web_status(self):
        ccman.log().info("Checking Bench Web Status")

        try:
            res    = req.get("http://{host}:{port}/api/ping".format(
                host = self.host.web,
                port = self.port.web
            ))
            status = res.ok
        except req.exceptions.ConnectionError:
            status = False

        return status

    def _check_app_status(self):
        ccman.log().info("Checking Bench App Status")

        try:
            res    = req.head("http://%s:%s" % (self.host.app, self.port.app))
            status = res.ok 
        except req.exceptions.ConnectionError:
            status = False

        return status

    def _check_db_status(self):
        ccman.log().info("Checking Bench DB Status")

        db      = get_db(host = self.host.db, port = self.port.db)

        try:
            db.query("SELECT 1+1 AS result")
            status = True
        except psycopg2.OperationalError:
            status = False

        return status

    def _check_cache_status(self):
        ccman.log().info("Checking Bench Cache Status")
        
        connection = get_redis_connection(
            host = self.host.cache,
            port = self.port.cache,

            refresh   = True,
            raise_err = False
        )

        return bool(connection)

    def _get_pg_envvars(self):
        envvars = dict(
            PGHOST = self.host.db,
            PGPORT = self.port.db
        )

        return envvars
    
    def __repr__(self):
        return "<Bench {name}>".format(
            name = self.name
        )

    def __eq__(self, other):
        if isinstance(other, Bench):
            return self.path == other.path
        else:
            return False