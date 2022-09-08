import pytest
import asyncio

from okite.wrap import Client

from _utils import start_server


ADDRESS = "127.0.0.1:8687"
start_server = pytest.fixture(autouse=True, scope="module")(
    start_server(ADDRESS))


def test_call():
    c = Client(ADDRESS)

    async def coro():
        r = await c.call("eval", "1")
        assert r == 1
    
    asyncio.run(coro())


def test_assign_from_local():
    c = Client(ADDRESS)

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
    c = Client(ADDRESS)

    async def coro():
        await c.op.assign_from_local("b", 100)
        await c.op.del_var("b")
        with pytest.raises(RuntimeError):
            await c.op.eval("b")

    asyncio.run(coro())


def test_register_from_local():
    c = Client(ADDRESS)

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
    c = Client(ADDRESS)

    async def coro():
        await c.op.register_from_local(lambda x: x + 1, "myadd")
        await c.op.unregister_func("myadd")
        with pytest.raises(RuntimeError):
            await c.call("myadd", 1)

    asyncio.run(coro())
