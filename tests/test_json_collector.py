from netbox_cable_audit.collectors.json import load_lldp_json


def test_load_lldp_json():
    connections = load_lldp_json("examples/lldp.json")

    assert len(connections) == 1

    connection = connections[0]

    assert connection.local_device == "sw-core-01"
    assert connection.local_interface == "Gi1/0/1"
    assert connection.remote_device == "sw-access-01"
    assert connection.remote_interface == "Gi1/0/48"
    assert connection.source == "lldp"
