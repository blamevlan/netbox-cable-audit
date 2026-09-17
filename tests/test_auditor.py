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

def test_multiple_connections():
    netbox = [
        Connection(
            local_device="sw-core-01",
            local_interface="Gi1/0/1",
            remote_device="sw-access-01",
            remote_interface="Gi1/0/48",
            source="netbox",
        ),
        Connection(
            local_device="sw-core-01",
            local_interface="Gi1/0/2",
            remote_device="sw-access-02",
            remote_interface="Gi1/0/48",
            source="netbox",
        ),
    ]

    lldp = [
        Connection(
            local_device="sw-core-01",
            local_interface="Gi1/0/1",
            remote_device="sw-access-01",
            remote_interface="Gi1/0/48",
            source="lldp",
        ),
        Connection(
            local_device="sw-core-01",
            local_interface="Gi1/0/2",
            remote_device="sw-access-03",
            remote_interface="Gi1/0/48",
            source="lldp",
        ),
    ]

    results = audit_connections(netbox, lldp)

    assert len(results) == 2
    assert results[0].status == "MATCH"
    assert results[1].status == "MISMATCH"

def test_matching_result_contains_connection_details():
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

    result = audit_connections(netbox, lldp)[0]

    assert result.local_device == "sw-core-01"
    assert result.local_interface == "Gi1/0/1"
    assert result.netbox_remote_device == "sw-access-01"
    assert result.netbox_remote_interface == "Gi1/0/48"
    assert result.lldp_remote_device == "sw-access-01"
    assert result.lldp_remote_interface == "Gi1/0/48"

def test_undocumented_result_contains_lldp_details():
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

    result = audit_connections(netbox, lldp)[0]

    assert result.local_device == "sw-core-01"
    assert result.local_interface == "Gi1/0/3"
    assert result.netbox_remote_device is None
    assert result.netbox_remote_interface is None
    assert result.lldp_remote_device == "ap-01"
    assert result.lldp_remote_interface == "eth0"


def test_not_detected_result_contains_netbox_details():
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

    result = audit_connections(netbox, lldp)[0]

    assert result.local_device == "sw-core-01"
    assert result.local_interface == "Gi1/0/4"
    assert result.netbox_remote_device == "server-01"
    assert result.netbox_remote_interface == "eth0"
    assert result.lldp_remote_device is None
    assert result.lldp_remote_interface is None
