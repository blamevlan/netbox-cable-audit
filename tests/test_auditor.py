from netbox_cable_audit.auditor import audit_connections
from netbox_cable_audit.models import Connection


def test_matching_connections():
    netbox = [
        Connection(
            local_device="sw-core-01",
            local_interface="Gi1/0/1",
            remote_device="sw-access-01",
            remote_interface="Gi1/0/48",
            source="netbox",
        )
    ]

    lldp = [
        Connection(
            local_device="sw-core-01",
            local_interface="Gi1/0/1",
            remote_device="sw-access-01",
            remote_interface="Gi1/0/48",
            source="lldp",
        )
    ]

    results = audit_connections(netbox, lldp)

    assert len(results) == 1
    assert results[0].status == "MATCH"

def test_mismatched_connections():
    netbox = [
        Connection(
            local_device="sw-core-01",
            local_interface="Gi1/0/2",
            remote_device="sw-access-02",
            remote_interface="Gi1/0/48",
            source="netbox",
        )
    ]

    lldp = [
        Connection(
            local_device="sw-core-01",
            local_interface="Gi1/0/2",
            remote_device="sw-access-03",
            remote_interface="Gi1/0/48",
            source="lldp",
        )
    ]

    results = audit_connections(netbox, lldp)

    assert len(results) == 1
    assert results[0].status == "MISMATCH"

def test_undocumented_connection():
    netbox = []

    lldp = [
        Connection(
            local_device="sw-core-01",
            local_interface="Gi1/0/3",
            remote_device="ap-01",
            remote_interface="eth0",
            source="lldp",
        )
    ]

    results = audit_connections(netbox, lldp)

    assert len(results) == 1
    assert results[0].status == "UNDOCUMENTED"

def test_not_detected_connection():
    netbox = [
        Connection(
            local_device="sw-core-01",
            local_interface="Gi1/0/4",
            remote_device="server-01",
            remote_interface="eth0",
            source="netbox",
        )
    ]

    lldp = []

    results = audit_connections(netbox, lldp)

    assert len(results) == 1
    assert results[0].status == "NOT_DETECTED"
