import typing as T
from .rpc.rpc import Server as _Server
from .rpc.rpc import Client as _Client

if T.TYPE_CHECKING:
    from .rpc.stream import Streamer


class Server(_Server):
    def __init__(
            self, address: str = "127.0.0.1:8686",
            streamer: T.Optional["Streamer"] = None) -> None:
        self.env = globals()

        def _assign_global(var: str, val: T.Any):
            self.env[var] = val

        def _register_func(func: T.Callable, key: T.Optional[str] = None):
            self.register_func(func, key)

        funcs: T.Dict[str, T.Callable] = {
            "exec": lambda e: exec(e, self.env),
            "eval": lambda e: eval(e, self.env),
            "print": print,
            "assign_global": _assign_global,
            "register_func": _register_func,
        }
        super().__init__(address, streamer, funcs)


class Client(_Client):
    def assign_from_local(self, var_name: str, val: T.Any):
        self.call("assign_global", var_name, val)

    def register_from_local(
            self, func: T.Callable, key: T.Optional[str] = None):
        self.call("register_func", func, key)

    def eval(self, expr: str):
        return self.call("eval", expr)
