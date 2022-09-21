import typing as T

import cloudpickle


class PicklerBase():

    def serialize(self, obj: T.Any) -> bytes:
        pass

    def deserialize(self, obj_bytes: bytes) -> T.Any:
        pass


class Pickler(PicklerBase):

    def serialize(self, obj: T.Any) -> bytes:
        return cloudpickle.dumps(obj)

    def deserialize(self, obj_bytes: bytes) -> T.Any:
        return cloudpickle.loads(obj_bytes)
