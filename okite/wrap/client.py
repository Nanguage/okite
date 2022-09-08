import uuid
import typing as T
from functools import wraps

from ..rpc.rpc import Client as _Client
from .proxy import Proxy, FuncProxy, ObjProxy
from ..utils import get_event_loop

if T.TYPE_CHECKING:
    from ..rpc.stream import Streamer


class Operations():
    def __init__(self, client: "Client"):
        self.client = client

    async def call(self, func_name, *args, **kwargs) -> T.Any:
        return await self.client.call(func_name, *args, **kwargs)

    async def assign_from_local(self, var_name: str, val: T.Any):
        await self.call("assign_global", var_name, val)

    async def del_var(self, var_name: str):
        await self.call("del_global", var_name)

    async def register_from_local(
            self, func: T.Callable, key: T.Optional[str] = None):
        await self.call("register_func", func, key)

    async def unregister_func(self, key: str):
        await self.call("unregister_func", key)

    async def eval(self, expr: str) -> T.Any:
        output = await self.call("eval", expr)
        return output

    async def exec(self, source: str):
        await self.call("exec", source)


def async_to_sync(async_func):
    @wraps(async_func)
    def sync_func(*args, **kwargs):
        with get_event_loop() as loop:
            coro = async_func(*args, **kwargs)
            res = loop.run_until_complete(coro)
        return res
    return sync_func


class SyncOperations(Operations):
    for name, obj in Operations.__dict__.items():
        if not name.startswith("__"):
            locals()[name] = async_to_sync(obj)


class Client(_Client):
    def __init__(self, address: str, streamer: T.Optional["Streamer"] = None):
        super().__init__(address, streamer)
        self.op = Operations(self)

    def __repr__(self) -> str:
        addr = self.server_addr
        return f"<Client address={addr[0]}:{addr[1]}>"

    def remote_func(self, func: T.Callable) -> "Proxy":
        p = FuncProxy(self, func.__name__)
        with get_event_loop() as loop:
            loop.run_until_complete(self.op.register_from_local(func))
        return p

    def remote_object(
            self, obj: T.Any,
            var_name: T.Optional[str] = None) -> "Proxy":
        if var_name is None:  # generate a random name
            rand_id = str(uuid.uuid4())[-8:]
            var_name = "var_" + rand_id
        p = ObjProxy(self, var_name)
        with get_event_loop() as loop:
            loop.run_until_complete(self.op.assign_from_local(var_name, obj))
        return p