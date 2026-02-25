# Service pointing to embedded routes on RPi

import requests
from typing import Any, Dict, Optional

class GatewayClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000", timeout: float = 5.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        try:
            response = requests.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
        except requests.RequestException as e:
            raise RuntimeError(f"Gateway connection failed: {e}")

        if not response.ok:
            raise RuntimeError(
                f"Gateway error {response.status_code}: {response.text}"
            )

        return response.json()

    def health(self) -> Dict[str, Any]:
        """
        GET /health
        """
        return self._request("GET", "/health")

    def get_devices(self) -> Dict[str, Any]:
        """
        GET /devices
        """
        return self._request("GET", "/devices")

    def get_device(self, device_id: str) -> Dict[str, Any]:
        """
        GET /devices/{device_id}
        """
        return self._request("GET", f"/devices/{device_id}")

    def set_device(
        self,
        device_id: str,
        state: str,
        user_id: Optional[str] = None,
        source: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        POST /devices/{device_id}/set
        """
        payload = {
            "state": state,
            "user_id": user_id,
            "source": source or "habit_engine",
        }

        return self._request(
            "POST",
            f"/devices/{device_id}/set",
            json=payload,
        )