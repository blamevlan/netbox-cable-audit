import requests

from netbox_cable_audit.models import Connection


class NetBoxClient:
    def __init__(self, base_url: str, token: str, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout

    def _headers(self):
        auth_type = "Bearer" if self.token.startswith("nbt_") else "Token"

        return {
            "Authorization": f"{auth_type} {self.token}",
            "Accept": "application/json",
        }

    def _get(self, path: str, params=None):
        if path.startswith(("http://", "https://")):
            url = path
        else:
            url = f"{self.base_url}{path}"

        response = requests.get(
            url,
            headers=self._headers(),
            params=params,
            timeout=self.timeout,
        )

        response.raise_for_status()
        return response.json()

    def _get_all(self, path: str, params=None):
        data = self._get(path, params=params)
        results = list(data["results"])

        while data.get("next"):
            data = self._get(data["next"])
            results.extend(data["results"])

        return results

    def get_device(self, name: str):
        data = self._get(
            "/api/dcim/devices/",
            params={"name": name},
        )

        results = data["results"]

        if not results:
            return None

        return results[0]

    def get_interface(self, device_id: int, name: str):
        data = self._get(
            "/api/dcim/interfaces/",
            params={
                "device_id": device_id,
                "name": name,
            },
        )

        results = data["results"]

        if not results:
            return None

        return results[0]

    def get_interfaces(self, device_id: int):
        return self._get_all(
            "/api/dcim/interfaces/",
            params={"device_id": device_id},
        )

    def trace_interface(self, interface_id: int):
        return self._get(
            f"/api/dcim/interfaces/{interface_id}/trace/"
        )

    def _connection_from_trace(
        self,
        local_device: str,
        local_interface: str,
        trace,
    ):
        if not trace:
            return None

        far_ends = trace[-1][2]

        if not far_ends:
            return None

        endpoint = far_ends[0]
        remote_device = endpoint.get("device")

        if not remote_device:
            return None

        return Connection(
            local_device=local_device,
            local_interface=local_interface,
            remote_device=remote_device["name"],
            remote_interface=endpoint["name"],
            source="netbox",
        )

    def get_connection(self, local_device: str, local_interface: str):
        device = self.get_device(local_device)

        if device is None:
            return None

        interface = self.get_interface(device["id"], local_interface)

        if interface is None:
            return None

        trace = self.trace_interface(interface["id"])

        return self._connection_from_trace(
            local_device,
            local_interface,
            trace,
        )

    def get_connections(self, local_device: str):
        device = self.get_device(local_device)

        if device is None:
            return []

        interfaces = self.get_interfaces(device["id"])
        connections = []

        for interface in interfaces:
            if interface.get("cable") is None:
                continue

            trace = self.trace_interface(interface["id"])

            connection = self._connection_from_trace(
                local_device,
                interface["name"],
                trace,
            )

            if connection is not None:
                connections.append(connection)

        return connections
