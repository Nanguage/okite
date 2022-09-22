import typing as T

import fire

from .wrap import Server
from .ssh import install_okite, launch_server
from .utils import find_free_port


def server(ip: str = "127.0.0.1", port: T.Optional[int] = None):
    if port is None:
        port = find_free_port()
    s = Server(f"{ip}:{port}")
    s.run()


fire.Fire({
    "server": server,
    "ssh_install": install_okite,
    "ssh_server": launch_server,
})
