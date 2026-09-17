from unittest.mock import Mock, patch

from netbox_cable_audit.netbox import NetBoxClient


@patch("netbox_cable_audit.netbox.requests.get")
def test_get_device_by_name(mock_get):
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "count": 1,
        "results": [
            {
                "id": 12,
                "name": "sw-core-01",
            }
        ],
    }
    mock_get.return_value = response

    client = NetBoxClient("https://netbox.example.com", "test-token")
    device = client.get_device("sw-core-01")

    assert device["id"] == 12
    assert device["name"] == "sw-core-01"


@patch("netbox_cable_audit.netbox.requests.get")
def test_get_interface_by_device_and_name(mock_get):
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "count": 1,
        "results": [
            {
                "id": 42,
                "name": "Gi1/0/1",
            }
        ],
    }
    mock_get.return_value = response

    client = NetBoxClient("https://netbox.example.com", "test-token")
    interface = client.get_interface(12, "Gi1/0/1")

    assert interface["id"] == 42
    assert interface["name"] == "Gi1/0/1"


@patch("netbox_cable_audit.netbox.requests.get")
def test_trace_interface(mock_get):
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = [
        [
            [{"id": 42, "name": "Gi1/0/1"}],
            {"id": 100},
            [{"id": 84, "name": "Gi1/0/48"}],
        ]
    ]
    mock_get.return_value = response

    client = NetBoxClient("https://netbox.example.com", "test-token")
    trace = client.trace_interface(42)

    assert trace[0][2][0]["id"] == 84


@patch("netbox_cable_audit.netbox.requests.get")
def test_v2_token_uses_bearer_authentication(mock_get):
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"count": 0, "results": []}
    mock_get.return_value = response

    client = NetBoxClient(
        "https://netbox.example.com",
        "nbt_example.secret",
    )
    client.get_device("missing-device")

    headers = mock_get.call_args.kwargs["headers"]

    assert headers["Authorization"] == "Bearer nbt_example.secret"

def test_get_connection_from_direct_trace():
    client = NetBoxClient("https://netbox.example.com", "test-token")

    client.get_device = Mock(
        return_value={"id": 12, "name": "sw-core-01"}
    )
    client.get_interface = Mock(
        return_value={"id": 42, "name": "Gi1/0/1"}
    )
    client.trace_interface = Mock(
        return_value=[
            [
                [
                    {
                        "id": 42,
                        "name": "Gi1/0/1",
                        "device": {"id": 12, "name": "sw-core-01"},
                    }
                ],
                {"id": 100},
                [
                    {
                        "id": 84,
                        "name": "Gi1/0/48",
                        "device": {"id": 20, "name": "sw-access-01"},
                    }
                ],
            ]
        ]
    )

    connection = client.get_connection("sw-core-01", "Gi1/0/1")

    assert connection.local_device == "sw-core-01"
    assert connection.local_interface == "Gi1/0/1"
    assert connection.remote_device == "sw-access-01"
    assert connection.remote_interface == "Gi1/0/48"
    assert connection.source == "netbox"


def test_get_connection_uses_end_of_patch_panel_trace():
    client = NetBoxClient("https://netbox.example.com", "test-token")

    client.get_device = Mock(
        return_value={"id": 12, "name": "sw-core-01"}
    )
    client.get_interface = Mock(
        return_value={"id": 42, "name": "Gi1/0/1"}
    )
    client.trace_interface = Mock(
        return_value=[
            [
                [{"id": 42, "name": "Gi1/0/1"}],
                {"id": 100},
                [{"id": 50, "name": "Front 1"}],
            ],
            [
                [{"id": 51, "name": "Rear 1"}],
                {"id": 101},
                [{"id": 60, "name": "Rear 24"}],
            ],
            [
                [{"id": 61, "name": "Front 24"}],
                {"id": 102},
                [
                    {
                        "id": 84,
                        "name": "Gi1/0/48",
                        "device": {"id": 20, "name": "sw-access-01"},
                    }
                ],
            ],
        ]
    )

    connection = client.get_connection("sw-core-01", "Gi1/0/1")

    assert connection.remote_device == "sw-access-01"
    assert connection.remote_interface == "Gi1/0/48"


def test_get_connection_returns_none_without_complete_trace():
    client = NetBoxClient("https://netbox.example.com", "test-token")

    client.get_device = Mock(
        return_value={"id": 12, "name": "sw-core-01"}
    )
    client.get_interface = Mock(
        return_value={"id": 42, "name": "Gi1/0/1"}
    )
    client.trace_interface = Mock(return_value=[])

    connection = client.get_connection("sw-core-01", "Gi1/0/1")

    assert connection is None
