# imports - standard imports
import os.path as osp

# imports - third-party imports
import git

# imports - module imports
import ccman

def run(*args, **kwargs):
    bench = kwargs.get("bench")

    path  = osp.join(bench.path, ".ccman")
    repo  = git.Repo(path)
    
    g     = repo.git
   
    g.fetch("origin")
    g.checkout("-B", "master", "--track", "origin/master")