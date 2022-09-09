import json

from okite.worker import Worker
from okite.wrap import Client
from okite.rpc.stream import Streamer, PicklerBase


def test_worker():
    addr = "127.0.0.1:8690"
    w = Worker(addr)
    c = Client(addr)
    w.start()
    assert c.sync_op.eval("1 + 1") == 2
    w.terminate()


def test_auto_addr():
    w = Worker()
    c = Client(w.server_addr)
    w.start()
    assert c.sync_op.eval("1 + 1") == 2
    w.terminate()


def test_with_block():
    with Worker() as w:
        c = Client(w.server_addr)
        assert c.sync_op.eval("1 + 1") == 2


def test_custom_pickler():
    class MyPickler(PicklerBase):
        def serialize(self, obj) -> bytes:
            return json.dumps(obj).encode()

        def deserialize(self, obj_bytes: bytes):
            return json.loads(obj_bytes.decode())

    streamer = Streamer(MyPickler())

    addr = "127.0.0.1:8691"
    w = Worker(addr, streamer=streamer)
    w.start()
    c = Client(addr, streamer=streamer)
    assert c.sync_op.eval("1 + 1") == 2
    w.terminate()
