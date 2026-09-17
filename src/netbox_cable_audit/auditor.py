from netbox_cable_audit.models import AuditResult, Connection

def _index_by_local_port(
    connections: list[Connection],
) -> dict[tuple[str, str], Connection]:
    return {
        (connection.local_device, connection.local_interface): connection
        for connection in connections
    }

def audit_connections(
    netbox_connections: list[Connection],
    lldp_connections: list[Connection],
) -> list[AuditResult]:
    netbox_by_port = _index_by_local_port(netbox_connections)
    lldp_by_port = _index_by_local_port(lldp_connections)
    ports = sorted(netbox_by_port.keys() | lldp_by_port.keys())
    results: list[AuditResult] = []

    for local_device, local_interface in ports:
        netbox = netbox_by_port.get((local_device, local_interface))
        lldp = lldp_by_port.get((local_device, local_interface))

        if netbox is None:
            results.append(AuditResult(
                status="UNDOCUMENTED",
                local_device=local_device,
                local_interface=local_interface,
                lldp_remote_device=lldp.remote_device,
                lldp_remote_interface=lldp.remote_interface,
            ))
            continue

        if lldp is None:
            results.append(AuditResult(
                status="NOT_DETECTED",
                local_device=local_device,
                local_interface=local_interface,
                netbox_remote_device=netbox.remote_device,
                netbox_remote_interface=netbox.remote_interface,
            ))
            continue

        same_remote = (
            netbox.remote_device == lldp.remote_device
            and netbox.remote_interface == lldp.remote_interface
        )
        results.append(AuditResult(
            status="MATCH" if same_remote else "MISMATCH",
            local_device=local_device,
            local_interface=local_interface,
            netbox_remote_device=netbox.remote_device,
            netbox_remote_interface=netbox.remote_interface,
            lldp_remote_device=lldp.remote_device,
            lldp_remote_interface=lldp.remote_interface,
        ))

    return results
