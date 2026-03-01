from __future__ import annotations

import json
from dataclasses import dataclass
from urllib import request


@dataclass
class PocketBaseClient:
    base_url: str
    admin_token: str | None = None

    def _headers(self) -> dict[str, str]:
        headers = {"content-type": "application/json"}
        if self.admin_token:
            headers["authorization"] = f"Bearer {self.admin_token}"
        return headers

    def create(self, collection: str, payload: dict) -> dict:
        req = request.Request(
            url=f"{self.base_url}/api/collections/{collection}/records",
            data=json.dumps(payload).encode("utf-8"),
            headers=self._headers(),
            method="POST",
        )
        with request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def list(self, collection: str, page: int = 1, per_page: int = 50) -> dict:
        req = request.Request(
            url=(
                f"{self.base_url}/api/collections/{collection}/records"
                f"?page={page}&perPage={per_page}"
            ),
            headers=self._headers(),
            method="GET",
        )
        with request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def update(self, collection: str, record_id: str, payload: dict) -> dict:
        req = request.Request(
            url=f"{self.base_url}/api/collections/{collection}/records/{record_id}",
            data=json.dumps(payload).encode("utf-8"),
            headers=self._headers(),
            method="PATCH",
        )
        with request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
