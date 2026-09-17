import json
from unittest.mock import Mock

from netbox_cable_audit.models import Connection
from netbox_cable_audit.runner import run_audit


def test_run_audit_collects_netbox_connections_for_lldp_devices(tmp_path):
    lldp_file = tmp_path / "lldp.json"
    lldp_file.write_text(
        json.dumps(
            {
                "sw-core-01": {
                    "Gi1/0/1": {
                        "remote_device": "sw-access-01",
                        "remote_interface": "Gi1/0/48"
                    }
                },
                "sw-core-02": {
                    "Gi1/0/1": {
                        "remote_device": "sw-access-02",
                        "remote_interface": "Gi1/0/48"
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    client = Mock()

    client.get_connections.side_effect = [
        [
            Connection(
                local_device="sw-core-01",
                local_interface="Gi1/0/1",
                remote_device="sw-access-01",
                remote_interface="Gi1/0/48",
                source="netbox",
            )
        ],
        [
            Connection(
                local_device="sw-core-02",
                local_interface="Gi1/0/1",
                remote_device="sw-access-03",
                remote_interface="Gi1/0/48",
                source="netbox",
            )
        ],
    ]

    results = run_audit(str(lldp_file), client)

    assert len(results) == 2
    assert results[0].status == "MATCH"
    assert results[1].status == "MISMATCH"

    client.get_connections.assert_any_call("sw-core-01")
    client.get_connections.assert_any_call("sw-core-02")
    assert client.get_connections.call_count == 2
