from dataclasses import dataclass


@dataclass(frozen=True)
class Connection:
    local_device: str
    local_interface: str
    remote_device: str
    remote_interface: str
    source: str


@dataclass(frozen=True)
class AuditResult:
    status: str
    local_device: str | None = None
    local_interface: str | None = None
    netbox_remote_device: str | None = None
    netbox_remote_interface: str | None = None
    lldp_remote_device: str | None = None
    lldp_remote_interface: str | None = None
