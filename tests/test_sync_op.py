import pytest

from okite.wrap import Client

from _utils import start_server


ADDRESS = "127.0.0.1:8689"
start_server = pytest.fixture(autouse=True, scope="session")(
    start_server(ADDRESS))
c = Client(ADDRESS)


def test_call():
    r = c.op.call("eval", "1")
    assert r == 1


def test_eval():
    r = c.op.eval("1")
    assert r == 1
    

def test_exec():
    c.op.exec("a = 10")
    r = c.op.eval("a")
    assert r == 10


def test_assign_from_local():
    c.op.assign_from_local("a", 100)
    assert c.op.eval("a") == 100
    c.op.assign_from_local("add1", lambda x: x + 1)
    assert c.op.eval("add1(1)") == 2

