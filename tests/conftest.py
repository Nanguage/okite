import sys
import platform
import asyncio


def pytest_sessionstart(session):
    sys.path.insert(0, "./")

    if "Windows" in platform.platform():
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())