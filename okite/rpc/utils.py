import typing as T


def parse_address(address: str) -> T.Tuple[str, int]:
    ip, port = address.split(":")
    port = int(port)
    return (ip, port)
