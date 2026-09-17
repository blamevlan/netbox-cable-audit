from urllib.parse import urlparse
import requests
from netbox_cable_audit.models import Connection

class NetBoxError(RuntimeError):
    pass

class NetBoxClient:
    def __init__(self, base_url: str, token: str, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.token = token.strip()
        self.timeout = timeout

    def _headers(self) -> dict[str, str]:
        auth_type = "Bearer" if self.token.startswith("nbt_") else "Token"
        return {
            "Authorization": f"{auth_type} {self.token}",
            "Accept": "application/json",
        }

    def _get(self, path: str, params=None):
        url = path if path.startswith(("http://", "https://")) else f"{self.base_url}{path}"
        try:
            response = requests.get(
                url,
                headers=self._headers(),
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise NetBoxError(f"NetBox request failed: {exc}") from exc
        try:
            return response.json()
        except ValueError as exc:
            raise NetBoxError("NetBox returned an invalid JSON response.") from exc

    def _get_all(self, path: str, params=None) -> list[dict]:
        data = self._get(path, params=params)
        if not isinstance(data, dict) or "results" not in data:
            raise NetBoxError("Unexpected NetBox list response.")
        results = list(data["results"])
        while data.get("next"):
            next_url = data["next"]
            parsed = urlparse(next_url)
            base_parsed = urlparse(self.base_url)
            if parsed.netloc and parsed.netloc != base_parsed.netloc:
                raise NetBoxError("NetBox pagination returned a URL for a different host.")
            data = self._get(next_url)
            results.extend(data["results"])
        return results

    def get_device(self, name: str):
        data = self._get("/api/dcim/devices/", params={"name": name})
        results = data.get("results", [])
        if not results:
            return None
        if len(results) > 1:
            raise NetBoxError(f"Multiple NetBox devices named '{name}' were found.")
        return results[0]

    def get_interface(self, device_id: int, name: str):
        data = self._get(
            "/api/dcim/interfaces/",
            params={"device_id": device_id, "name": name},
        )
        results = data.get("results", [])
        if not results:
            return None
        if len(results) > 1:
            raise NetBoxError(
                f"Multiple interfaces named '{name}' were found on device ID {device_id}."
            )
        return results[0]

    def get_interfaces(self, device_id: int) -> list[dict]:
        return self._get_all(
            "/api/dcim/interfaces/",
            params={"device_id": device_id},
        )

    def trace_interface(self, interface_id: int):
        return self._get(f"/api/dcim/interfaces/{interface_id}/trace/")

    @staticmethod
    def _connection_from_trace(
        local_device: str,
        local_interface: str,
        trace,
    ) -> Connection | None:
        if not trace:
            return None
        try:
            far_ends = trace[-1][2]
        except (IndexError, TypeError) as exc:
            raise NetBoxError("Unexpected NetBox cable trace response.") from exc
        if not far_ends:
            return None
        endpoint = far_ends[0]
        if not isinstance(endpoint, dict):
            raise NetBoxError("Unexpected NetBox cable trace endpoint.")
        remote_device = endpoint.get("device")
        remote_name = endpoint.get("name")
        if not remote_device or not remote_name:
            return None
        device_name = remote_device.get("name") or remote_device.get("display")
        if not device_name:
            return None
        return Connection(
            local_device=local_device,
            local_interface=local_interface,
            remote_device=device_name,
            remote_interface=remote_name,
            source="netbox",
        )

    def get_connection(
        self,
        local_device: str,
        local_interface: str,
    ) -> Connection | None:
        device = self.get_device(local_device)
        if device is None:
            return None
        interface = self.get_interface(device["id"], local_interface)
        if interface is None:
            return None
        return self._connection_from_trace(
            local_device,
            local_interface,
            self.trace_interface(interface["id"]),
        )

    def get_connections(self, local_device: str) -> list[Connection]:
        device = self.get_device(local_device)
        if device is None:
            return []
        connections: list[Connection] = []
        for interface in self.get_interfaces(device["id"]):
            if interface.get("cable") is None:
                continue
            connection = self._connection_from_trace(
                local_device,
                interface["name"],
                self.trace_interface(interface["id"]),
            )
            if connection is not None:
                connections.append(connection)
        return connections
