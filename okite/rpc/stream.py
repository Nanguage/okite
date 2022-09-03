import typing as T
import cloudpickle
import struct
import io


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


class Streamer:

    OBJLEN_PACK_FORMAT = '<Q'

    def __init__(self, pickler: T.Optional[Pickler] = None) -> None:
        if pickler is None:
            self.pickler = Pickler()
        else:
            self.pickler = pickler

    def load(self, file: io.BufferedReader):
        size, = struct.unpack(self.OBJLEN_PACK_FORMAT, file.read(8))
        obj_bytes = file.read(size)
        obj = self.pickler.deserialize(obj_bytes)
        return obj

    def dump(self, obj: T.Any, file: io.BufferedWriter):
        obj_bytes = self.pickler.serialize(obj)
        file.write(struct.pack(self.OBJLEN_PACK_FORMAT, len(obj_bytes)))
        file.write(obj_bytes)
