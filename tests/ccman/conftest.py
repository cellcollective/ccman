# imports - compatibility imports
from   six.moves import SimpleHTTPServer, socketserver

# imports - standard imports
import os
import os.path as osp
import threading

# imports - third-party imports
import pytest

# imports - module imports
import ccman

class HTTPServer:
    def __init__(self):
        self.handler = SimpleHTTPServer.SimpleHTTPRequestHandler

    def run(self, host = "127.0.0.1", port = 8000, thread = False):
        if not thread:
            server_ = socketserver.TCPServer((host, port), self.handler)
            server_.serve_forever()
        else:
            self.thread = threading.Thread(target = self.run, kwargs = dict(host = host, port = port, thread = False), daemon = True)
            self.thread.start()

@pytest.fixture()
def server():
    server_ = HTTPServer()
    yield server_

@pytest.fixture()
def bench(tmpdir):
    tmp   = tmpdir.mkdir("tmp")
    path  = osp.join(str(tmp), "ccbench")

    bench = ccman.Bench(path)
    bench.create()
    
    return bench