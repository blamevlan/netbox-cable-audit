from unittest.mock import Mock, patch
import pytest

from netbox_cable_audit.netbox import NetBoxClient, NetBoxError

@patch("netbox_cable_audit.netbox.requests.get")
def test_v2_token_uses_bearer_authentication(mock_get):
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"count": 0, "results": []}
    mock_get.return_value = response

    client = NetBoxClient("https://netbox.example.com", "nbt_example.secret")
    client.get_device("missing-device")

    assert mock_get.call_args.kwargs["headers"]["Authorization"] == "Bearer nbt_example.secret"

@patch("netbox_cable_audit.netbox.requests.get")
def test_v1_token_uses_token_authentication(mock_get):
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"count": 0, "results": []}
    mock_get.return_value = response

    client = NetBoxClient("https://netbox.example.com", "legacy-token")
    client.get_device("missing-device")

    assert mock_get.call_args.kwargs["headers"]["Authorization"] == "Token legacy-token"

@patch("netbox_cable_audit.netbox.requests.get")
def test_get_interfaces_handles_pagination(mock_get):
    first = Mock()
    first.raise_for_status.return_value = None
    first.json.return_value = {
        "count": 2,
        "next": "https://netbox.example.com/api/dcim/interfaces/?device_id=12&offset=1",
        "results": [{"id": 42, "name": "Gi1/0/1"}],
    }

    second = Mock()
    second.raise_for_status.return_value = None
    second.json.return_value = {
        "count": 2,
        "next": None,
        "results": [{"id": 43, "name": "Gi1/0/2"}],
    }

    mock_get.side_effect = [first, second]

    interfaces = NetBoxClient(
        "https://netbox.example.com",
        "test-token",
    ).get_interfaces(12)

    assert [item["id"] for item in interfaces] == [42, 43]

def test_connection_from_direct_trace():
    trace = [[
        [{"id": 42, "name": "Gi1/0/1", "device": {"name": "sw-core-01"}}],
        {"id": 100},
        [{"id": 84, "name": "Gi1/0/48", "device": {"name": "sw-access-01"}}],
    ]]

    result = NetBoxClient._connection_from_trace(
        "sw-core-01",
        "Gi1/0/1",
        trace,
    )

    assert result.remote_device == "sw-access-01"
    assert result.remote_interface == "Gi1/0/48"

def test_connection_uses_last_endpoint_of_patch_panel_trace():
    trace = [
        [
            [{"id": 42, "name": "Gi1/0/1"}],
            {"id": 100},
            [{"id": 50, "name": "F1", "device": {"name": "patch-01"}}],
        ],
        [
            [{"id": 51, "name": "R1", "device": {"name": "patch-01"}}],
            {"id": 101},
            [{"id": 60, "name": "R1", "device": {"name": "patch-02"}}],
        ],
        [
            [{"id": 61, "name": "F1", "device": {"name": "patch-02"}}],
            {"id": 102},
            [{"id": 84, "name": "Gi1/0/48", "device": {"name": "sw-access-01"}}],
        ],
    ]

    result = NetBoxClient._connection_from_trace(
        "sw-core-01",
        "Gi1/0/1",
        trace,
    )

    assert result.remote_device == "sw-access-01"
    assert result.remote_interface == "Gi1/0/48"

def test_empty_trace_returns_none():
    assert NetBoxClient._connection_from_trace(
        "sw-core-01",
        "Gi1/0/1",
        [],
    ) is None

def test_malformed_trace_raises_clear_error():
    with pytest.raises(NetBoxError, match="Unexpected NetBox cable trace"):
        NetBoxClient._connection_from_trace(
            "sw-core-01",
            "Gi1/0/1",
            [["bad"]],
        )

def test_get_connections_skips_interfaces_without_cable():
    client = NetBoxClient("https://netbox.example.com", "test-token")
    client.get_device = Mock(return_value={"id": 12, "name": "sw-core-01"})
    client.get_interfaces = Mock(return_value=[
        {"id": 42, "name": "Gi1/0/1", "cable": {"id": 100}},
        {"id": 43, "name": "Gi1/0/2", "cable": None},
    ])
    client.trace_interface = Mock(return_value=[[
        [{"id": 42, "name": "Gi1/0/1"}],
        {"id": 100},
        [{"id": 84, "name": "Gi1/0/48", "device": {"name": "sw-access-01"}}],
    ]])

    connections = client.get_connections("sw-core-01")

    assert len(connections) == 1
    assert connections[0].remote_device == "sw-access-01"
    assert client.trace_interface.call_count == 1
