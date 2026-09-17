from netbox_cable_audit.auditor import audit_connections
from netbox_cable_audit.collectors.json import load_lldp_json


def run_audit(lldp_path: str, netbox_client):
    lldp_connections = load_lldp_json(lldp_path)

    local_devices = sorted(
        {connection.local_device for connection in lldp_connections}
    )

    netbox_connections = []

    for device in local_devices:
        netbox_connections.extend(
            netbox_client.get_connections(device)
        )

    return audit_connections(
        netbox_connections,
        lldp_connections,
    )
