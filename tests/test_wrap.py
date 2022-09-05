import pytest
import multiprocessing

from okite.wrap import Server, Client


ADDRESS = "127.0.0.1:8687"


def _run_server():
    s = Server(ADDRESS)
    s.run_server()


@pytest.fixture(autouse=True, scope="module")
def start_server():
    p = multiprocessing.Process(target=_run_server)
    p.start()
    yield
    p.terminate()


def test_call():
    c = Client(ADDRESS)
    assert c.call("eval", "1") == 1


def test_assign_from_local():
    c = Client(ADDRESS)
    assert c.eval("1") == 1
    c.assign_from_local("a", 100)
    assert c.eval("a") == 100
    c.assign_from_local("add1", lambda x: x + 1)
    assert c.eval("add1(1)") == 2


def test_register_from_local():
    c = Client(ADDRESS)

    def add2(x):
        return x + 2

    c.register_from_local(add2)
    assert c.call("add2", 1) == 3
    c.register_from_local(lambda x: x + 3, key="add3")
    assert c.call("add3", 1) == 4
