from netbox_cable_audit.models import Connection

def test_connection_stores_endpoints():
    connection = Connection(
        local_device="sw-core-01",
        local_interface="Gi1/0/1",
        remote_device="sw-access-01",
        remote_interface="Gi1/0/48",
        source="lldp",
    )
    assert connection.local_device == "sw-core-01"
    assert connection.local_interface == "Gi1/0/1"
    assert connection.remote_device == "sw-access-01"
    assert connection.remote_interface == "Gi1/0/48"
    assert connection.source == "lldp"
