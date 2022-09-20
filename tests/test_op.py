import pytest
import asyncio

from okite.wrap import Client, Server

from _utils import start_server


ADDRESS = "127.0.0.1:8687"
start_server = pytest.fixture(autouse=True, scope="session")(
    start_server(ADDRESS))
c = Client(ADDRESS)


def test_wrap_server():
    s = Server(ADDRESS)

    def add1(x):
        return x + 1
    s.register_func(add1)


def test_call():
    async def coro():
        r = await c.call("eval", "1")
        assert r == 1
        r = await c.op.call("eval", "1")
        assert r == 1
    
    asyncio.run(coro())


def test_assign_from_local():
    async def coro():
        r = await c.op.eval("1")
        assert r == 1
        await c.op.assign_from_local("a", 100)
        r = await c.op.eval("a")
        assert r == 100
        await c.op.assign_from_local("add1", lambda x: x + 1)
        r = await c.op.eval("add1(1)")
        assert r == 2

    asyncio.run(coro())


def test_del_var():
    async def coro():
        await c.op.assign_from_local("b", 100)
        await c.op.del_var("b")
        with pytest.raises(RuntimeError):
            await c.op.eval("b")

    asyncio.run(coro())


def test_register_from_local():
    def add2(x):
        return x + 2

    async def coro():
        await c.op.register_from_local(add2)
        r = await c.call("add2", 1)
        assert r == 3
        await c.op.register_from_local(lambda x: x + 3, key="add3")
        r = await c.call("add3", 1)
        assert r == 4

    asyncio.run(coro())


def test_unregister_func():
    async def coro():
        await c.op.register_from_local(lambda x: x + 1, "myadd")
        await c.op.unregister_func("myadd")
        with pytest.raises(RuntimeError):
            await c.call("myadd", 1)

    asyncio.run(coro())


def test_set_get_attr():
    class A():
        def __init__(self) -> None:
            self.a = 1

    a = A()

    async def coro():
        await c.op.assign_from_local("a", a)
        a_a = await c.op.get_attr("a", "a")
        assert a_a == 1
        await c.op.set_attr("a", "b", 2)
        a_b = await c.op.get_attr("a", "b")
        assert a_b == 2

    asyncio.run(coro())


def test_import_module():
    async def coro():
        await c.op.import_module("time")
        await c.op.eval("time.time()")
        await c.op.import_module("os.path", "osp")
        await c.op.eval("osp.abspath('./')")

    asyncio.run(coro())
