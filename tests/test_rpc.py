import pytest
import multiprocessing
import asyncio
import json

from okite.rpc.rpc import Server, Client, get_handler
from okite.rpc.stream import Streamer
from okite.rpc.pickler import PicklerBase
from okite.utils import patch_multiprocessing_pickler
from okite.utils import wait_until_bind


ADDRESS = "127.0.0.1:8686"
c = Client(ADDRESS)


def _run_server():
    s = Server(ADDRESS)
    s.register_func(eval)
    s.run()


@pytest.fixture(scope="session", autouse=True)
def start_server():
    p = multiprocessing.Process(target=_run_server)
    p.start()
    wait_until_bind(ADDRESS)
    yield
    p.terminate()


def test_create_handler():
    s = Streamer()
    get_handler({}, s)


def test_create_server():
    s = Server(ADDRESS)
    s.register_func(eval)


def test_call():
    async def coro():
        s_ = 'Hello World!'
        r_ = await c.call("eval", repr(s_))
        assert r_ == s_
    asyncio.run(coro())


def test_custom_pickler_1():
    patch_multiprocessing_pickler()

    class MyPickler(PicklerBase):
        def serialize(self, obj) -> bytes:
            return json.dumps(obj).encode()

        def deserialize(self, obj_bytes: bytes):
            return json.loads(obj_bytes.decode())

    streamer = Streamer(MyPickler())
    addr = "127.0.0.1:8685"
    def _run_server():
        s = Server(addr, streamer=streamer)
        s.register_func(eval)
        s.run()

    p = multiprocessing.Process(target=_run_server)
    p.start()
    wait_until_bind(addr)
    c = Client(addr, streamer=streamer)
    assert asyncio.run(c.call("eval", "1")) == 1
    p.terminate()


def test_custom_pickler_2():
    patch_multiprocessing_pickler()

    class MyPickler(PicklerBase):
        def serialize(self, obj) -> bytes:
            return json.dumps(obj).encode()

        def deserialize(self, obj_bytes: bytes):
            return json.loads(obj_bytes.decode())

    addr = "127.0.0.1:8678"
    def _run_server():
        s = Server(addr, pickler_cls=MyPickler)
        s.register_func(eval)
        s.run()

    p = multiprocessing.Process(target=_run_server)
    p.start()
    wait_until_bind(addr)
    c = Client(addr, pickler_cls=MyPickler)
    assert asyncio.run(c.call("eval", "1")) == 1
    p.terminate()
