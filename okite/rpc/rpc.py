import typing as T
import socketserver
import traceback
from socket import socket

from .stream import Streamer
from .utils import parse_address


def get_handler_class(calls, streamer: Streamer):

    class Handler(socketserver.StreamRequestHandler):

        def handle(self):
            func = streamer.load(self.rfile)
            args = streamer.load(self.rfile)
            kwargs = streamer.load(self.rfile)
            try:
                output = calls[func](*args, **kwargs)
            except Exception:
                # signal error, write stacktrace
                streamer.dump(True, self.wfile)
                streamer.dump(traceback.format_exc(), self.wfile)
            else:
                # write output
                streamer.dump(False, self.wfile)
                streamer.dump(output, self.wfile)

    return Handler


class Server():
    def __init__(
            self, address: str = "127.0.0.1:8686",
            streamer: T.Optional[Streamer] = None,
            funcs: T.Optional[T.Dict[str, T.Callable]] = None) -> None:
        if funcs is None:
            funcs = {}
        self.funcs = funcs
        self.address = parse_address(address)
        if streamer is None:
            self.streamer = Streamer()
        else:
            self.streamer = streamer

    def register_func(self, func: T.Callable, key=None):
        if key is None:
            key = func.__name__
        self.funcs[key] = func

    def run_server(self):
        handler_cls = get_handler_class(self.funcs, self.streamer)
        ss = socketserver.TCPServer(self.address, handler_cls)
        print(f"Start server at {self.address}")
        ss.serve_forever()


class Client():
    def __init__(
            self, address: str,
            streamer: T.Optional[Streamer] = None) -> None:
        if streamer is not None:
            self.streamer = streamer
        else:
            self.streamer = Streamer()
        self.server_addr = parse_address(address)

    def call(self, func_name: str, *args, **kwargs):
        sock = socket()
        sock.connect(self.server_addr)
        file = sock.makefile(mode='rwb', buffering=-1)
        # write function name and arguments
        self.streamer.dump(func_name, file)
        self.streamer.dump(args, file)
        self.streamer.dump(kwargs, file)
        file.flush()
        # check for error
        if self.streamer.load(file):
            raise RuntimeError(self.streamer.load(file))
        # read output
        return self.streamer.load(file)
