from okite.wrap import Server
import multiprocessing


def _run_server(addr):
    s = Server(addr)
    s.run()


def start_server(addr):
    def wrap():
        p = multiprocessing.Process(target=_run_server, args=(addr,))
        p.start()
        yield
        p.terminate()

    return wrap
