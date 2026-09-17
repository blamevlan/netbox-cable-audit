import json
from pathlib import Path
from netbox_cable_audit.models import Connection

class LldpInputError(ValueError):
    pass

def _load_document(path: str) -> dict:
    file_path = Path(path)
    try:
        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError as exc:
        raise LldpInputError(f"LLDP file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise LldpInputError(
            f"Invalid JSON in {path}: line {exc.lineno}, column {exc.colno}"
        ) from exc
    if not isinstance(data, dict):
        raise LldpInputError("LLDP JSON root must be an object.")
    return data

def load_lldp_devices(path: str) -> list[str]:
    data = _load_document(path)
    for device, interfaces in data.items():
        if not isinstance(device, str) or not device:
            raise LldpInputError("Device names must be non-empty strings.")
        if not isinstance(interfaces, dict):
            raise LldpInputError(f"Interfaces for device '{device}' must be an object.")
    return sorted(data.keys())

def load_lldp_json(path: str) -> list[Connection]:
    data = _load_document(path)
    connections: list[Connection] = []
    for local_device, interfaces in data.items():
        if not isinstance(local_device, str) or not local_device:
            raise LldpInputError("Device names must be non-empty strings.")
        if not isinstance(interfaces, dict):
            raise LldpInputError(f"Interfaces for device '{local_device}' must be an object.")
        for local_interface, neighbor in interfaces.items():
            if not isinstance(neighbor, dict):
                raise LldpInputError(
                    f"Neighbor data for {local_device} {local_interface} must be an object."
                )
            try:
                remote_device = neighbor["remote_device"]
                remote_interface = neighbor["remote_interface"]
            except KeyError as exc:
                raise LldpInputError(
                    f"Missing {exc.args[0]!r} for {local_device} {local_interface}."
                ) from exc
            if not all(isinstance(v, str) and v for v in (
                local_interface, remote_device, remote_interface
            )):
                raise LldpInputError(
                    f"Connection fields for {local_device} {local_interface} "
                    "must be non-empty strings."
                )
            connections.append(Connection(
                local_device=local_device,
                local_interface=local_interface,
                remote_device=remote_device,
                remote_interface=remote_interface,
                source="lldp",
            ))
    return connections
