import typing as T
from multiprocessing import Process

from .wrap import Server
from .rpc.stream import Streamer
from .rpc.pickler import Pickler
from .rpc.transport import Transport
from .utils import find_free_port, wait_until_bind, parse_address
from .utils import patch_multiprocessing_pickler


patch_multiprocessing_pickler()


class Worker(Process):
    def __init__(
            self, address: T.Optional[str] = None,
            pickler_cls: type = Pickler,
            transport_cls: type = Transport,
            streamer: T.Optional[Streamer] = None,
            ) -> None:
        if address is None:
            port = find_free_port()
            self.server_addr = f"127.0.0.1:{port}"
        else:
            self.server_addr = address
        self.pickler_cls = pickler_cls
        self.transport_cls = transport_cls
        self.streamer = streamer
        super().__init__()

    def run(self):
        server = Server(
            self.server_addr, 
            pickler_cls=self.pickler_cls,
            transport_cls=self.transport_cls,
            streamer=self.streamer,
            )
        server.run()

    def wait_until_server_bind(self):
        wait_until_bind(parse_address(self.server_addr))

    def __enter__(self):
        self.start()
        self.wait_until_server_bind()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.terminate()
