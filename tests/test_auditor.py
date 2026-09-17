from netbox_cable_audit.auditor import audit_connections
from netbox_cable_audit.models import Connection

def connection(local_interface, remote_device, remote_interface, source):
    return Connection(
        local_device="sw-core-01",
        local_interface=local_interface,
        remote_device=remote_device,
        remote_interface=remote_interface,
        source=source,
    )

def test_matching_connections():
    results = audit_connections(
        [connection("Gi1/0/1", "sw-access-01", "Gi1/0/48", "netbox")],
        [connection("Gi1/0/1", "sw-access-01", "Gi1/0/48", "lldp")],
    )
    assert results[0].status == "MATCH"

def test_mismatched_connections():
    results = audit_connections(
        [connection("Gi1/0/2", "sw-access-02", "Gi1/0/48", "netbox")],
        [connection("Gi1/0/2", "sw-access-03", "Gi1/0/48", "lldp")],
    )
    assert results[0].status == "MISMATCH"

def test_undocumented_connection_contains_lldp_details():
    result = audit_connections(
        [],
        [connection("Gi1/0/3", "ap-01", "eth0", "lldp")],
    )[0]

    assert result.status == "UNDOCUMENTED"
    assert result.local_interface == "Gi1/0/3"
    assert result.netbox_remote_device is None
    assert result.lldp_remote_device == "ap-01"

def test_not_detected_connection_contains_netbox_details():
    result = audit_connections(
        [connection("Gi1/0/4", "server-01", "eth0", "netbox")],
        [],
    )[0]

    assert result.status == "NOT_DETECTED"
    assert result.netbox_remote_device == "server-01"
    assert result.lldp_remote_device is None

def test_multiple_connections_are_matched_by_local_port_not_list_order():
    netbox = [
        connection("Gi1/0/2", "sw-access-02", "Gi1/0/48", "netbox"),
        connection("Gi1/0/1", "sw-access-01", "Gi1/0/48", "netbox"),
    ]
    lldp = [
        connection("Gi1/0/1", "sw-access-01", "Gi1/0/48", "lldp"),
        connection("Gi1/0/2", "sw-access-03", "Gi1/0/48", "lldp"),
    ]

    results = audit_connections(netbox, lldp)

    assert [result.status for result in results] == ["MATCH", "MISMATCH"]
