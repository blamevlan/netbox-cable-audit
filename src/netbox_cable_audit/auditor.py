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
            results.append(
                AuditResult(
                    status="UNDOCUMENTED",
                    local_device=lldp.local_device,
                    local_interface=lldp.local_interface,
                    lldp_remote_device=lldp.remote_device,
                    lldp_remote_interface=lldp.remote_interface,
                )
            )
            continue

        if lldp is None:
            results.append(
                AuditResult(
                    status="NOT_DETECTED",
                    local_device=netbox.local_device,
                    local_interface=netbox.local_interface,
                    netbox_remote_device=netbox.remote_device,
                    netbox_remote_interface=netbox.remote_interface,
                )
            )
            continue

        same_remote = (
            netbox.remote_device == lldp.remote_device
            and netbox.remote_interface == lldp.remote_interface
        )

        status = "MATCH" if same_remote else "MISMATCH"

        results.append(
            AuditResult(
                status=status,
                local_device=netbox.local_device,
                local_interface=netbox.local_interface,
                netbox_remote_device=netbox.remote_device,
                netbox_remote_interface=netbox.remote_interface,
                lldp_remote_device=lldp.remote_device,
                lldp_remote_interface=lldp.remote_interface,
            )
        )

    return results
