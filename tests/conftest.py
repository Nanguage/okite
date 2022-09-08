import sys
import os.path
import platform
import asyncio


def pytest_sessionstart(session):
    sys.path.insert(0, "./")
    sys.path.insert(0, os.path.dirname(__file__))

    if "Windows" in platform.platform():
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
