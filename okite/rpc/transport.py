import socket
import typing as T
import asyncio


class TransportBase():
    def __init__(self, address: T.Tuple[str, int], server=True) -> None:
        self.address = address
        self.is_server = server


class Transport(TransportBase):
    def __init__(self, address: T.Tuple[str, int], server=True) -> None:
        super().__init__(address, server)
        if server:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind(address)
            self.sock.listen()
            self.sock.setblocking(False)

    async def init_connection(self):
        loop = asyncio.get_event_loop()
        if self.is_server:
            self.conn, _ = await loop.sock_accept(self.sock)
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            await loop.sock_connect(self.sock, self.address)
            self.conn = self.sock

    async def write(self, data: bytes):
        loop = asyncio.get_event_loop()
        await loop.sock_sendall(self.conn, data)

    async def read(self, n: int) -> bytes:
        loop = asyncio.get_event_loop()
        return await loop.sock_recv(self.conn, n)

    def close_connection(self):
        self.conn.close()
