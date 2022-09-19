from okite.wrap import Server
import multiprocessing
from okite.utils import wait_until_bind


def _run_server(addr):
    s = Server(addr)
    s.run()


def start_server(addr):
    def wrap():
        p = multiprocessing.Process(target=_run_server, args=(addr,))
        p.start()
        wait_until_bind(addr)
        yield
        p.terminate()

    return wrap
