import pytest

from okite.wrap import Client

from _utils import start_server


ADDRESS = "127.0.0.1:8689"
start_server = pytest.fixture(autouse=True, scope="module")(
    start_server(ADDRESS))
c = Client(ADDRESS)


def test_call():
    r = c.sync_op.call("eval", "1")
    assert r == 1


def test_eval():
    r = c.sync_op.eval("1")
    assert r == 1
    

def test_exec():
    c.sync_op.exec("a = 10")
    r = c.sync_op.eval("a")
    assert r == 10


def test_assign_from_local():
    c.sync_op.assign_from_local("a", 100)
    assert c.sync_op.eval("a") == 100
    c.sync_op.assign_from_local("add1", lambda x: x + 1)
    assert c.sync_op.eval("add1(1)") == 2

