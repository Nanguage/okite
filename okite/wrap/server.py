import typing as T

from ..rpc.rpc import Server as _Server
from ..rpc.transport import Transport


if T.TYPE_CHECKING:
    from ..rpc.stream import Streamer


class Server(_Server):
    def __init__(
            self, address: str = "127.0.0.1:8686",
            streamer: T.Optional["Streamer"] = None,
            transport_cls: type = Transport,
            ) -> None:
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

        def _get_attr(
                obj_name: str, attr_name: str, default: T.Any = None) -> T.Any:
            obj = self.env[obj_name]
            return getattr(obj, attr_name, default)

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
            "get_attr": _get_attr,
            "set_attr": _set_attr,
        }
        super().__init__(address, streamer, transport_cls, funcs)
