import pytest
import multiprocessing

from okite.rpc.rpc import Server, Client


ADDRESS = "127.0.0.1:8686"


def _run_server():
    s = Server(ADDRESS)
    s.register_func(eval)
    s.register_func(exec)
    s.run_server()


@pytest.fixture(autouse=True, scope="module")
def start_server():
    p = multiprocessing.Process(target=_run_server)
    p.start()
    yield
    p.terminate()


def test_call():
    c = Client(ADDRESS)
    s_ = 'Hello World!'
    r_ = c.call("eval", repr(s_))
    assert r_ == s_

