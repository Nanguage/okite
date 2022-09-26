import time

from okite.worker import Worker
from okite import Client


def bench_hello_world():
    N = 1000
    with Worker() as worker:
        c = Client(worker.server_addr)
        t0 = time.time()
        for _ in range(N):
            c.op.eval("'Hello World!'")
        t1 = time.time()
        delta = t1 - t0
        print(f"Run hello_world {N} times")
        print(f"cost: {delta}s, {delta/N}s per run")
        print(f"QPS: {1/(delta/N)}")


def bench_numpy_add():
    import numpy as np
    N = 100
    a = np.zeros(shape=(1000, 1000))
    b = np.ones(shape=(1000, 1000))
    with Worker() as worker:
        c = Client(worker.server_addr)
        c.op.register_from_local(lambda a, b: a + b, "add")
        t0 = time.time()
        for _ in range(N):
            c.op.call("add", a, b)
        t1 = time.time()
        delta = t1 - t0
        print(f"Run numpy_add {N} times")
        print(f"cost: {delta}s, {delta/N}s per run")
        print(f"QPS: {1/(delta/N)}")


if __name__ == "__main__":
    bench_hello_world()
    bench_numpy_add()
