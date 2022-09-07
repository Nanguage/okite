import types
import uuid
import typing as T

from .rpc.rpc import Server as _Server
from .rpc.rpc import Client as _Client
from .utils import get_event_loop

if T.TYPE_CHECKING:
    from .rpc.stream import Streamer


class Server(_Server):
    def __init__(
            self, address: str = "127.0.0.1:8686",
            streamer: T.Optional["Streamer"] = None) -> None:
        self.env = globals()

        def _assign_global(var: str, val: T.Any):
            self.env[var] = val

        def _del_global(var: str):
            self.env.pop(var)

        def _register_func(func: T.Callable, key: T.Optional[str] = None):
            self.register_func(func, key)

        def _unregister_func(key: str):
            self.unregister_func(key)

        def _call_method(
                obj_name: str, method_name: str,
                *args, **kwargs) -> T.Any:
            obj = self.env[obj_name]
            mth = getattr(obj, method_name)
            output = mth(*args, **kwargs)
            return output

        def _set_attr(obj_name: str, attr_name: str, value: T.Any):
            obj = self.env[obj_name]
            setattr(obj, attr_name, value)

        funcs: T.Dict[str, T.Callable] = {
            "exec": lambda e: exec(e, self.env),
            "eval": lambda e: eval(e, self.env),
            "print": print,
            "assign_global": _assign_global,
            "del_global": _del_global,
            "register_func": _register_func,
            "unregister_func": _unregister_func,
            "call_method": _call_method,
            "set_attr": _set_attr,
        }
        super().__init__(address, streamer, funcs)


class Proxy():
    def __init__(self, client: "Client", name: str) -> None:
        self.client = client
        self.name = name

    def __repr__(self) -> str:
        r = f"<{self.__class__.__name__} " \
            f"name={self.name} client={self.client}>"
        return r


class FuncProxy(Proxy):
    def __call__(self, *args, **kwargs):
        with get_event_loop() as loop:
            coro = self.client.call(self.name, *args, **kwargs)
            output = loop.run_until_complete(coro)
        return output

    def clear(self):
        with get_event_loop() as loop:
            coro = self.client.unregister_func(self.name)
            loop.run_until_complete(coro)


class MethodProxy(Proxy):
    def __init__(
            self, client: "Client",
            obj_name: str, mth_name: str) -> None:
        self.obj_name = obj_name
        self.mth_name = mth_name
        super().__init__(client, obj_name)

    def __call__(self, *args, **kwargs):
        with get_event_loop() as loop:
            coro = self.client.call(
                "call_method", self.obj_name, self.mth_name,
                *args, **kwargs)
            output = loop.run_until_complete(coro)
        return output


class ObjProxy(Proxy):
    def clear(self):
        with get_event_loop() as loop:
            coro = self.client.del_var(self.name)
            loop.run_until_complete(coro)

    def __getattr__(self, name: str) -> T.Any:
        async def coro():
            attr = await self.client.eval(f"{self.name}.{name}")
            if isinstance(attr, types.MethodType):
                return MethodProxy(self.client, self.name, name)
            else:
                return attr
        with get_event_loop() as loop:
            return loop.run_until_complete(coro())

    def __setattr__(self, name: str, value: T.Any):
        if name in ('client', 'name'):
            super().__setattr__(name, value)
        else:
            with get_event_loop() as loop:
                coro = self.client.call("set_attr", self.name, name, value)
                loop.run_until_complete(coro)


class Client(_Client):
    def __repr__(self) -> str:
        addr = self.server_addr
        return f"<Client address={addr[0]}:{addr[1]}>"

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

    def remote_func(self, func: T.Callable) -> "Proxy":
        p = FuncProxy(self, func.__name__)
        with get_event_loop() as loop:
            loop.run_until_complete(self.register_from_local(func))
        return p

    def remote_object(
            self, obj: T.Any,
            var_name: T.Optional[str] = None) -> "Proxy":
        if var_name is None:  # generate a random name
            rand_id = str(uuid.uuid4())[-8:]
            var_name = "var_" + rand_id
        p = ObjProxy(self, var_name)
        with get_event_loop() as loop:
            loop.run_until_complete(self.assign_from_local(var_name, obj))
        return p
