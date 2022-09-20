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

    async def dump(self, obj: T.Any, file: Transport):
        obj_bytes = self.pickler.serialize(obj)
        await file.write(struct.pack(self.OBJLEN_PACK_FORMAT, len(obj_bytes)))
        await file.write(obj_bytes)
