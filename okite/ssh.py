import typing as T
import socket

import paramiko
from paramiko.buffered_pipe import PipeTimeout


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
        remote_python_path = "python"
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
        remote_python_path = "python"
    cmd = f"{remote_python_path} -m okite server --port={server_port}"
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
    stdout.close()
    stderr.close()
