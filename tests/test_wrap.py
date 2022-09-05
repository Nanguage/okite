import pytest
import multiprocessing
import asyncio

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
