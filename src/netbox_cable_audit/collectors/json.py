import json

from netbox_cable_audit.models import Connection


def load_lldp_json(path: str) -> list[Connection]:
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    connections = []

    for local_device, interfaces in data.items():
        for local_interface, neighbor in interfaces.items():
            connections.append(
                Connection(
                    local_device=local_device,
                    local_interface=local_interface,
                    remote_device=neighbor["remote_device"],
                    remote_interface=neighbor["remote_interface"],
                    source="lldp",
                )
            )

    return connections
