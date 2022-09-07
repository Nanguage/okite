import typing as T
import traceback
import asyncio

from .stream import Streamer
from .utils import parse_address


def get_handler(calls, streamer: Streamer):

    async def handler(
            reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        func = await streamer.load(reader)
        args = await streamer.load(reader)
        kwargs = await streamer.load(reader)
        try:
            output = calls[func](*args, **kwargs)
        except Exception:
            streamer.dump(True, writer)
            streamer.dump(traceback.format_exc(), writer)
        else:
            streamer.dump(False, writer)
            streamer.dump(output, writer)
        await writer.drain()

    return handler


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

    def unregister_func(self, key: str):
        self.funcs.pop(key)

    def run(self):
        handler = get_handler(self.funcs, self.streamer)

        async def server_coro():
            print(f"Start server at {self.address}")
            server = await asyncio.start_server(handler, *self.address)
            async with server:
                await server.serve_forever()

        asyncio.run(server_coro())


class Client():
    def __init__(
            self, address: str,
            streamer: T.Optional[Streamer] = None) -> None:
        if streamer is not None:
            self.streamer = streamer
        else:
            self.streamer = Streamer()
        self.server_addr = parse_address(address)

    async def call(self, func_name: str, *args, **kwargs):
        reader, writer = await asyncio.open_connection(
            self.server_addr[0], self.server_addr[1])
        self.streamer.dump(func_name, writer)
        self.streamer.dump(args, writer)
        self.streamer.dump(kwargs, writer)
        await writer.drain()
        flag = await self.streamer.load(reader)
        if flag:
            error_msg = await self.streamer.load(reader)
            raise RuntimeError(error_msg)
        output = await self.streamer.load(reader)
        return output
