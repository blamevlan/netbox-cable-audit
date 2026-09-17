import requests


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
        response = requests.get(
            f"{self.base_url}{path}",
            headers=self._headers(),
            params=params,
            timeout=self.timeout,
        )

        response.raise_for_status()
        return response.json()

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

    def trace_interface(self, interface_id: int):
        return self._get(
            f"/api/dcim/interfaces/{interface_id}/trace/"
        )
