import pytest
import multiprocessing
import asyncio
import json

from okite.rpc.rpc import Server, Client
from okite.rpc.stream import Streamer, PicklerBase
from okite.utils import patch_multiprocessing_pickler


ADDRESS = "127.0.0.1:8686"
c = Client(ADDRESS)


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
    async def coro():
        s_ = 'Hello World!'
        r_ = await c.call("eval", repr(s_))
        assert r_ == s_
    asyncio.run(coro())


def test_custom_pickler():
    patch_multiprocessing_pickler()

    class MyPickler(PicklerBase):
        def serialize(self, obj) -> bytes:
            return json.dumps(obj).encode()

        def deserialize(self, obj_bytes: bytes):
            return json.loads(obj_bytes.decode())

    streamer = Streamer(MyPickler())
    def _run_server():
        s = Server("127.0.0.1:8685", streamer=streamer)
        s.register_func(eval)
        s.run()

    p = multiprocessing.Process(target=_run_server)
    p.start()

    c = Client("127.0.0.1:8685", streamer=streamer)
    assert asyncio.run(c.call("eval", "1")) == 1
    p.terminate()
