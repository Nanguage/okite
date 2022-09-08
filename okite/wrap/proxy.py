import typing as T
import types

from ..utils import get_event_loop
if T.TYPE_CHECKING:
    from .client import Client


class Proxy():
    def __init__(self, client: "Client", name: str) -> None:
        self._client = client
        self._name = name

    def __repr__(self) -> str:
        r = f"<{self.__class__.__name__} " \
            f"name={self._name} client={self._client}>"
        return r


class FuncProxy(Proxy):
    def __call__(self, *args, **kwargs):
        with get_event_loop() as loop:
            coro = self._client.call(self._name, *args, **kwargs)
            output = loop.run_until_complete(coro)
        return output

    def clear(self):
        with get_event_loop() as loop:
            coro = self._client.op.unregister_func(self._name)
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
            coro = self._client.call(
                "call_method", self.obj_name, self.mth_name,
                *args, **kwargs)
            output = loop.run_until_complete(coro)
        return output


class ObjProxy(Proxy):
    def clear(self):
        with get_event_loop() as loop:
            coro = self._client.op.del_var(self._name)
            loop.run_until_complete(coro)

    def __getattr__(self, name: str) -> T.Any:
        async def coro():
            attr = await self._client.op.eval(f"{self._name}.{name}")
            if isinstance(attr, types.MethodType):
                return MethodProxy(self._client, self._name, name)
            else:
                return attr
        with get_event_loop() as loop:
            return loop.run_until_complete(coro())

    def __setattr__(self, name: str, value: T.Any):
        if name in ('_client', '_name'):
            super().__setattr__(name, value)
        else:
            with get_event_loop() as loop:
                coro = self._client.call("set_attr", self._name, name, value)
                loop.run_until_complete(coro)
