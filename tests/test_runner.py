import json
from unittest.mock import Mock

from netbox_cable_audit.models import Connection
from netbox_cable_audit.runner import run_audit

def test_run_audit_keeps_device_without_lldp_neighbors_in_scope(tmp_path):
    path = tmp_path / "lldp.json"
    path.write_text(json.dumps({
        "sw-core-01": {
            "Gi1/0/1": {
                "remote_device": "sw-access-01",
                "remote_interface": "Gi1/0/48",
            }
        },
        "sw-core-02": {},
    }), encoding="utf-8")

    client = Mock()
    client.get_connections.side_effect = [
        [Connection(
            local_device="sw-core-01",
            local_interface="Gi1/0/1",
            remote_device="sw-access-01",
            remote_interface="Gi1/0/48",
            source="netbox",
        )],
        [Connection(
            local_device="sw-core-02",
            local_interface="Gi1/0/1",
            remote_device="server-02",
            remote_interface="eth0",
            source="netbox",
        )],
    ]

    results = run_audit(str(path), client)

    assert [result.status for result in results] == ["MATCH", "NOT_DETECTED"]
    assert client.get_connections.call_count == 2
