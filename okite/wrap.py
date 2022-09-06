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

        def _del_global(var: str) -> bool:
            if var in self.env:
                self.env.pop(var)
                return True
            else:
                return False

        def _register_func(func: T.Callable, key: T.Optional[str] = None):
            self.register_func(func, key)

        def _unregister_func(key: str) -> bool:
            return self.unregister_func(key)

        funcs: T.Dict[str, T.Callable] = {
            "exec": lambda e: exec(e, self.env),
            "eval": lambda e: eval(e, self.env),
            "print": print,
            "assign_global": _assign_global,
            "del_global": _del_global,
            "register_func": _register_func,
            "unregister_func": _unregister_func,
        }
        super().__init__(address, streamer, funcs)


class Proxy():
    def __init__(self, client: "Client", name: str) -> None:
        self.client = client
        self.name = name

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name} client={self.client}>"

    def __call__(self, *args, **kwargs):
        with get_event_loop() as loop:
            coro = self.client.call(self.name, *args, **kwargs)
            output = loop.run_until_complete(coro)
        return output

    def __del__(self):
        with get_event_loop() as loop:
            loop.run_until_complete(self.client.unregister_func(self.name))


class Client(_Client):
    def __repr__(self) -> str:
        addr = self.server_addr
        return f"<Client address={addr[0]}:{addr[1]}>"

    async def assign_from_local(self, var_name: str, val: T.Any):
        await self.call("assign_global", var_name, val)

    async def del_var(self, var_name: str) -> bool:
        return await self.call("del_global", var_name)

    async def register_from_local(
            self, func: T.Callable, key: T.Optional[str] = None):
        await self.call("register_func", func, key)

    async def unregister_func(self, key: str) -> bool:
        return await self.call("unregister_func", key)

    async def eval(self, expr: str) -> T.Any:
        output = await self.call("eval", expr)
        return output

    async def exec(self, source: str):
        await self.call("exec", source)

    def remote_func(self, func: T.Callable) -> "Proxy":
        p = Proxy(self, func.__name__)
        with get_event_loop() as loop:
            loop.run_until_complete(self.register_from_local(func))
        return p
