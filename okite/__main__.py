import fire
from .wrap import Server


def server(ip="127.0.0.1", port=8686):
    s = Server(f"{ip}:{port}")
    s.run()


fire.Fire({
    "server": server
})
