import typing as T
import socket

import paramiko
from paramiko.buffered_pipe import PipeTimeout

from .utils import parse_address
from .worker import Worker


def _get_client(
        host, username, port=22,
        password=None, key_filename=None,
        ) -> paramiko.SSHClient:
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.connect(
        hostname=host,
        port=port,
        username=username,
        password=password,
        key_filename=key_filename,
    )
    return client


def install_okite(
        host, username, port=22,
        password=None, key_filename=None,
        remote_python_path=None,
        ):
    """Install a okite on remote machine, via SSH."""
    client = _get_client(host, username, port, password, key_filename)
    if remote_python_path is None:
        remote_python_path = "/bin/env python"
    cmd = f"{remote_python_path} -m pip install okite"
    _, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode()
    if out:
        print(out)
    err = stderr.read().decode()
    if err:
        print(err)


def launch_server(
        host, username, server_port: T.Optional[int] = None,
        ssh_port=22,
        password=None, key_filename=None,
        remote_python_path=None,
        ):
    """Launch a okite server on remote machine, via SSH."""
    client = _get_client(host, username, ssh_port, password, key_filename)
    if remote_python_path is None:
        remote_python_path = "/bin/env python"
    cmd = f"{remote_python_path} -m okite server " + \
          f"--ip='0.0.0.0' --port={server_port}"
    _, stdout, stderr = client.exec_command(cmd)

    stdout.channel.settimeout(0.1)
    stderr.channel.settimeout(0.1)
    while True:
        try:
            out = stdout.read().decode()
            if out:
                print(out)
            else:
                err = stderr.read().decode()
                print(err)
                break
        except (PipeTimeout, socket.timeout):
            continue


class SSHWorker(Worker):
    def __init__(
            self, address: str,
            remote_python_path: T.Optional[str] = None,
            ssh_kwargs: T.Optional[dict] = None,
            ) -> None:
        super().__init__(address, type, type, None)
        host, port = parse_address(address)
        self.port = port
        self.remote_python_path = remote_python_path
        if ssh_kwargs is None:
            ssh_kwargs = dict()
        ssh_kwargs.update({'host': host})
        self.ssh_kwargs = ssh_kwargs

    def run(self):
        ssh_kwargs = self.ssh_kwargs
        launch_server(
            ssh_kwargs['host'],
            ssh_kwargs['username'],
            self.port,
            ssh_kwargs.get("port", 22),
            ssh_kwargs.get("password"),
            ssh_kwargs.get("key_filename"),
            self.remote_python_path,
        )
