from dataclasses import dataclass


@dataclass(frozen=True)
class Connection:
    local_device: str
    local_interface: str
    remote_device: str
    remote_interface: str
    source: str
