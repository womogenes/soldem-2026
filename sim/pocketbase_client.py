from __future__ import annotations

import json
from dataclasses import dataclass
from urllib import parse
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

    def _request(
        self,
        method: str,
        path: str,
        payload: dict | None = None,
        query: dict[str, int | str] | None = None,
    ) -> dict:
        query_str = ""
        if query:
            query_str = "?" + parse.urlencode(query)
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        req = request.Request(
            url=f"{self.base_url}{path}{query_str}",
            data=data,
            headers=self._headers(),
            method=method,
        )
        with request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}

    def auth_superuser(self, email: str, password: str) -> dict:
        payload = {"identity": email, "password": password}
        out = self._request(
            "POST",
            "/api/collections/_superusers/auth-with-password",
            payload=payload,
        )
        token = out.get("token")
        if token:
            self.admin_token = token
        return out

    def create(self, collection: str, payload: dict) -> dict:
        return self._request(
            "POST",
            f"/api/collections/{collection}/records",
            payload=payload,
        )

    def list(self, collection: str, page: int = 1, per_page: int = 50) -> dict:
        return self._request(
            "GET",
            f"/api/collections/{collection}/records",
            query={"page": page, "perPage": per_page},
        )

    def update(self, collection: str, record_id: str, payload: dict) -> dict:
        return self._request(
            "PATCH",
            f"/api/collections/{collection}/records/{record_id}",
            payload=payload,
        )
