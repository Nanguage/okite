import typing as T
import struct

import cloudpickle


from .transport import Transport


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
        self._bytes: T.Optional[bytes] = None
        self._cache_obj: T.Optional[T.Any] = None
        if pickler is None:
            self.pickler = Pickler()
        else:
            self.pickler = pickler

    async def load(self, file: Transport):
        size_byte = await file.read(8)
        size, = struct.unpack(self.OBJLEN_PACK_FORMAT, size_byte)
        received_size = 0
        byte_chunks = []
        while received_size < size:
            chunk = await file.read(size - received_size)
            received_size += len(chunk)
            byte_chunks.append(chunk)
        obj_bytes = b"".join(byte_chunks)
        obj = self.pickler.deserialize(obj_bytes)
        return obj

    def pre_serialize(self, obj: T.Any):
        self._bytes = self.pickler.serialize(obj)
        self._cache_obj = obj

    async def dump(self, obj: T.Any, file: Transport):
        if (self._cache_obj is not obj) or (self._bytes is None):
            obj_bytes = self.pickler.serialize(obj)
        else:
            obj_bytes = self._bytes
            self._bytes = None
            self._cache_obj = None
        await file.write(struct.pack(self.OBJLEN_PACK_FORMAT, len(obj_bytes)))
        await file.write(obj_bytes)
