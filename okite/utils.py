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
