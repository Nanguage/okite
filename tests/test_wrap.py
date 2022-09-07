import pytest
import multiprocessing
import asyncio

from okite.wrap import Server, Client


ADDRESS = "127.0.0.1:8687"


def _run_server():
    s = Server(ADDRESS)
    s.run()


@pytest.fixture(autouse=True, scope="module")
def start_server():
    p = multiprocessing.Process(target=_run_server)
    p.start()
    yield
    p.terminate()


def test_call():
    c = Client(ADDRESS)

    async def coro():
        r = await c.call("eval", "1")
        assert r == 1
    
    asyncio.run(coro())


def test_assign_from_local():
    c = Client(ADDRESS)

    async def coro():
        r = await c.eval("1")
        assert r == 1
        await c.assign_from_local("a", 100)
        r = await c.eval("a")
        assert r == 100
        await c.assign_from_local("add1", lambda x: x + 1)
        r = await c.eval("add1(1)")
        assert r == 2

    asyncio.run(coro())


def test_del_var():
    c = Client(ADDRESS)

    async def coro():
        await c.assign_from_local("b", 100)
        await c.del_var("b")
        with pytest.raises(RuntimeError):
            await c.eval("b")

    asyncio.run(coro())


def test_register_from_local():
    c = Client(ADDRESS)

    def add2(x):
        return x + 2

    async def coro():
        await c.register_from_local(add2)
        r = await c.call("add2", 1)
        assert r == 3
        await c.register_from_local(lambda x: x + 3, key="add3")
        r = await c.call("add3", 1)
        assert r == 4

    asyncio.run(coro())


def test_unregister_func():
    c = Client(ADDRESS)

    async def coro():
        await c.register_from_local(lambda x: x + 1, "myadd")
        await c.unregister_func("myadd")
        with pytest.raises(RuntimeError):
            await c.call("myadd", 1)

    asyncio.run(coro())


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
    r = asyncio.run(c.eval("b.mth1(10)"))
    assert r == 20
    p.c = "111"
    assert asyncio.run(c.eval("b.c")) == "111"
