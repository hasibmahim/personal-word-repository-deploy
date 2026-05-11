"""HTTP client wrapper for the auxiliary study-pack service."""

from __future__ import annotations

from typing import Any

import requests


class StudyPackError(RuntimeError):
    """Raised when the auxiliary service returns an error response."""

    def __init__(self, status_code: int, message: str):
        super().__init__(message)
        self.status_code = status_code


class StudyPackClient:
    """Small wrapper around the auxiliary study-pack service."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def random_pack(self, user_id: str, count: int = 5) -> dict[str, Any]:
        return self._request(
            "GET",
            "/study-pack/random",
            params={"user_id": user_id, "count": count},
        )

    def missing_translations_pack(self, user_id: str) -> dict[str, Any]:
        return self._request(
            "GET",
            "/study-pack/missing-translations",
            params={"user_id": user_id},
        )

    def category_pack(self, user_id: str, category_id: str) -> dict[str, Any]:
        return self._request(
            "GET",
            "/study-pack/by-category",
            params={"user_id": user_id, "category_id": category_id},
        )

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        try:
            response = self.session.request(
                method,
                f"{self.base_url}{path}",
                timeout=10,
                **kwargs,
            )
        except requests.RequestException as exc:
            raise StudyPackError(0, f"Could not reach study-pack service: {exc}") from exc

        try:
            payload = response.json()
        except ValueError:
            payload = response.text

        if not response.ok:
            if isinstance(payload, dict):
                message = payload.get("error") or payload.get("message") or str(payload)
            else:
                message = str(payload)
            raise StudyPackError(response.status_code, f"{response.status_code}: {message}")

        return payload
