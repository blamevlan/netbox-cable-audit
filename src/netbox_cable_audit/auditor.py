from netbox_cable_audit.models import AuditResult


def audit_connections(netbox_connections, lldp_connections):
    if not netbox_connections and lldp_connections:
        return [AuditResult(status="UNDOCUMENTED")]

    if netbox_connections and not lldp_connections:
        return [AuditResult(status="NOT_DETECTED")]

    netbox = netbox_connections[0]
    lldp = lldp_connections[0]

    same_remote = (
        netbox.remote_device == lldp.remote_device
        and netbox.remote_interface == lldp.remote_interface
    )

    if same_remote:
        return [AuditResult(status="MATCH")]

    return [AuditResult(status="MISMATCH")]
