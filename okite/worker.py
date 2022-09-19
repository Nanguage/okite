import typing as T
from multiprocessing import Process

from .wrap import Server
from .rpc.stream import Streamer
from .utils import find_free_port
from .utils import patch_multiprocessing_pickler


class Worker(Process):
    def __init__(
            self, address: T.Optional[str] = None,
            streamer: T.Optional[Streamer] = None) -> None:
        if address is None:
            port = find_free_port()
            self.server_addr = f"127.0.0.1:{port}"
        else:
            self.server_addr = address
        if streamer is not None:
            patch_multiprocessing_pickler()
        self.streamer = streamer
        super().__init__()

    def run(self):
        server = Server(self.server_addr, streamer=self.streamer)
        server.run()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.terminate()