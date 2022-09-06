import pytest
import multiprocessing
import asyncio

from okite.rpc.rpc import Server, Client


ADDRESS = "127.0.0.1:8686"


def _run_server():
    s = Server(ADDRESS)
    s.register_func(eval)
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
        s_ = 'Hello World!'
        r_ = await c.call("eval", repr(s_))
        assert r_ == s_
    asyncio.run(coro())

