import typing as T
import time
import socket
import asyncio
import contextlib


@contextlib.contextmanager
def get_event_loop():
    is_new_loop = False
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        is_new_loop = True
    try:
        yield loop
    finally:
        if is_new_loop:
            loop.close()


def patch_multiprocessing_pickler():
    import pickle
    import cloudpickle
    from multiprocessing import reduction
    pickle.Pickler = cloudpickle.Pickler
    reduction.ForkingPickler = cloudpickle.Pickler


def find_free_port():
    """https://stackoverflow.com/a/45690594/8500469"""
    with contextlib.closing(
            socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        port = s.getsockname()[1]
    return port


def parse_address(address: str) -> T.Tuple[str, int]:
    ip, port = address.split(":")
    port_ = int(port)
    return (ip, port_)


def is_port_in_use(host: str, port: int) -> bool:
    """Check if the port is in use.
    https://stackoverflow.com/a/52872579/8500469
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0


def wait_until_bind(
        server_addr: T.Union[str, T.Tuple[str, int]],
        time_delta: float = 0.01):
    if isinstance(server_addr, str):
        server_addr = parse_address(server_addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        if is_port_in_use(*server_addr):
            break
        else:
            time.sleep(time_delta)
    sock.close()
