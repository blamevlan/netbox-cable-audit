import json
import pytest

from netbox_cable_audit.collectors.json import (
    LldpInputError,
    load_lldp_devices,
    load_lldp_json,
)

def test_load_lldp_json(tmp_path):
    path = tmp_path / "lldp.json"
    path.write_text(json.dumps({
        "sw-core-01": {
            "Gi1/0/1": {
                "remote_device": "sw-access-01",
                "remote_interface": "Gi1/0/48",
            }
        }
    }), encoding="utf-8")

    connections = load_lldp_json(str(path))

    assert len(connections) == 1
    assert connections[0].local_device == "sw-core-01"
    assert connections[0].source == "lldp"

def test_load_lldp_devices_keeps_device_without_neighbors(tmp_path):
    path = tmp_path / "lldp.json"
    path.write_text(json.dumps({"sw-core-01": {}}), encoding="utf-8")

    assert load_lldp_devices(str(path)) == ["sw-core-01"]
    assert load_lldp_json(str(path)) == []

def test_missing_neighbor_field_is_clear_error(tmp_path):
    path = tmp_path / "lldp.json"
    path.write_text(json.dumps({
        "sw-core-01": {
            "Gi1/0/1": {"remote_device": "sw-access-01"}
        }
    }), encoding="utf-8")

    with pytest.raises(LldpInputError, match="remote_interface"):
        load_lldp_json(str(path))

def test_invalid_json_is_clear_error(tmp_path):
    path = tmp_path / "lldp.json"
    path.write_text("{ nope", encoding="utf-8")

    with pytest.raises(LldpInputError, match="Invalid JSON"):
        load_lldp_json(str(path))
