from netbox_cable_audit.models import AuditResult


def audit_connections(netbox_connections, lldp_connections):
    netbox_by_port = {
        (connection.local_device, connection.local_interface): connection
        for connection in netbox_connections
    }

    lldp_by_port = {
        (connection.local_device, connection.local_interface): connection
        for connection in lldp_connections
    }

    ports = netbox_by_port.keys() | lldp_by_port.keys()
    results = []

    for port in sorted(ports):
        netbox = netbox_by_port.get(port)
        lldp = lldp_by_port.get(port)

        if netbox is None:
            results.append(AuditResult(status="UNDOCUMENTED"))
            continue

        if lldp is None:
            results.append(AuditResult(status="NOT_DETECTED"))
            continue

        same_remote = (
            netbox.remote_device == lldp.remote_device
            and netbox.remote_interface == lldp.remote_interface
        )

        if same_remote:
            results.append(AuditResult(status="MATCH"))
        else:
            results.append(AuditResult(status="MISMATCH"))

    return results
