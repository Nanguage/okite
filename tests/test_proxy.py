import pytest
import asyncio

from okite.wrap import Client

from _utils import start_server


ADDRESS = "127.0.0.1:8688"
start_server = pytest.fixture(autouse=True, scope="session")(
    start_server(ADDRESS))


def test_remote_func():
    c = Client(ADDRESS)
    
    @c.remote_func
    def add10(x):
        return x + 10

    assert add10(10) == 20

    @c.remote_func
    def add(a, b):
        return a + b

    assert add(1, 2) == 3


def test_remote_obj():
    c = Client(ADDRESS)

    class A():
        def __init__(self):
            self.a = 10
        
        def mth1(self, x):
            return self.a + x

    a = A()
    p = c.remote_object(a)
    assert p.a == 10
    assert p.mth1(10) == 20
    b = A()
    p = c.remote_object(b, "b")
    r = asyncio.run(c.async_op.eval("b.mth1(10)"))
    assert r == 20
    p.c = "111"
    assert asyncio.run(c.async_op.eval("b.c")) == "111"
