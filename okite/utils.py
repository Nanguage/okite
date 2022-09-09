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
