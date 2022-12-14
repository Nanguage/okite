import typing as T
import traceback
import asyncio
import signal

from .pickler import Pickler
from .stream import Streamer
from ..utils import parse_address, get_event_loop
from .transport import Transport


def get_handler(calls, streamer: Streamer):

    async def handler(transport: Transport):
        try:
            command = await streamer.load(transport)
        except Exception:
            transport.close_connection()
            return

        if command == "call":
            func = await streamer.load(transport)
            args = await streamer.load(transport)
            kwargs = await streamer.load(transport)
            try:
                output = calls[func](*args, **kwargs)
            except Exception:
                await streamer.dump(True, transport)  # flag
                await streamer.dump(traceback.format_exc(), transport)
            else:
                try:
                    streamer.pre_serialize(output)
                except Exception:
                    await streamer.dump(True, transport)  # flag
                    await streamer.dump(traceback.format_exc(), transport)
                else:
                    await streamer.dump(False, transport)  # flag
                    await streamer.dump(output, transport)
        else:
            print(f"unsupported command: {command}, close the connection.")
        transport.close_connection()

    return handler


class Server():
    def __init__(
            self, address: str = "127.0.0.1:8686",
            pickler_cls: type = Pickler,
            transport_cls: type = Transport,
            streamer: T.Optional[Streamer] = None,
            funcs: T.Optional[T.Dict[str, T.Callable]] = None) -> None:
        if funcs is None:
            funcs = {}
        self.funcs = funcs
        self.address = parse_address(address)
        if streamer is None:
            self.streamer = Streamer(pickler_cls())
        else:
            self.streamer = streamer
        self.transport_cls = transport_cls

    def register_func(self, func: T.Callable, key=None):
        if key is None:
            key = func.__name__
        self.funcs[key] = func

    def unregister_func(self, key: str):
        self.funcs.pop(key)

    def run(self):
        transport: Transport = self.transport_cls(self.address, True)
        handler = get_handler(self.funcs, self.streamer)

        async def server_coro():
            print(f"Start server at {self.address}", flush=True)
            loop = asyncio.get_event_loop()

            while True:
                await transport.init_connection()
                loop.create_task(handler(transport))

        with get_event_loop() as loop:
            signal.signal(signal.SIGINT, lambda s, f: loop.stop())
            loop.run_until_complete(server_coro())


class Client():
    def __init__(
            self, address: str,
            pickler_cls: type = Pickler,
            transport_cls: type = Transport,
            streamer: T.Optional[Streamer] = None,
            ) -> None:
        if streamer is not None:
            self.streamer = streamer
        else:
            self.streamer = Streamer(pickler_cls())
        self.server_addr = parse_address(address)
        self.transport: Transport = transport_cls(self.server_addr, False)

    async def call(self, func_name: str, *args, **kwargs):
        await self.transport.init_connection()
        await self.streamer.dump("call", self.transport)
        await self.streamer.dump(func_name, self.transport)
        await self.streamer.dump(args, self.transport)
        await self.streamer.dump(kwargs, self.transport)
        flag = await self.streamer.load(self.transport)
        if flag:
            error_msg = await self.streamer.load(self.transport)
            raise RuntimeError(error_msg)
        output = await self.streamer.load(self.transport)
        self.transport.close_connection()
        return output
