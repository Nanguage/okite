import json

from okite.worker import Worker
from okite.wrap import Client
from okite.rpc.pickler import PicklerBase
from okite.rpc.stream import Streamer


def test_worker():
    addr = "127.0.0.1:8690"
    w = Worker(addr)
    c = Client(addr)
    w.start()
    w.wait_until_server_bind()
    assert c.op.eval("1 + 1") == 2
    w.terminate()


def test_auto_addr():
    w = Worker()
    c = Client(w.server_addr)
    w.start()
    w.wait_until_server_bind()
    assert c.op.eval("1 + 1") == 2
    w.terminate()


def test_with_block():
    with Worker() as w:
        c = Client(w.server_addr)
        assert c.op.eval("1 + 1") == 2
    with Worker() as w1, Worker() as w2:
        c = Client(w1.server_addr)
        assert c.op.eval("1 + 1") == 2
        c = Client(w2.server_addr)
        assert c.op.eval("1 + 1") == 2


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
    w.wait_until_server_bind()
    c = Client(addr, pickler_cls=MyPickler)
    assert c.op.eval("1 + 1") == 2
    w.terminate()
