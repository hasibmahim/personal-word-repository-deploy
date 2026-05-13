"""HTTP client wrapper for talking to the Personal Word Repository API."""

from __future__ import annotations

from typing import Any

import requests


class ApiError(RuntimeError):
    """Raised when the API returns an error response."""

    def __init__(self, status_code: int, message: str):
        super().__init__(message)
        self.status_code = status_code


class WordRepositoryApiClient:
    """Small wrapper around the REST API using a shared requests session."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    def healthz(self) -> dict[str, Any]:
        """Check whether the API is reachable."""
        return self._request("GET", "/healthz")

    def create_user(self, email: str, password: str) -> dict[str, Any]:
        return self._request(
            "POST",
            "/users",
            json={"email": email, "password": password},
        )

    def get_user(self, user_id: str) -> dict[str, Any]:
        return self._request("GET", f"/users/{user_id}")

    def list_parts_of_speech(self) -> list[dict[str, Any]]:
        return self._request("GET", "/parts-of-speech")

    def create_word(
        self,
        user_id: str,
        text: str,
        language: str,
        part_of_speech_id: int,
        category_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        payload = {
            "text": text,
            "language": language,
            "user_id": user_id,
            "part_of_speech_id": part_of_speech_id,
        }
        if category_ids is not None:
            payload["category_ids"] = category_ids
        return self._request("POST", "/words", json=payload)

    def list_words(
        self,
        *,
        user_id: str | None = None,
        category_id: str | None = None,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {}
        if user_id is not None:
            params["user_id"] = user_id
        if category_id is not None:
            params["category_id"] = category_id
        return self._request("GET", "/words", params=params or None)

    def get_word(self, word_id: str) -> dict[str, Any]:
        return self._request("GET", f"/words/{word_id}")

    def update_word(
        self,
        word_id: str,
        *,
        user_id: str,
        text: str,
        language: str,
        part_of_speech_id: int,
        category_ids: list[str],
    ) -> dict[str, Any]:
        payload = {
            "user_id": user_id,
            "text": text,
            "language": language,
            "part_of_speech_id": part_of_speech_id,
            "category_ids": category_ids,
        }
        return self._request("PUT", f"/words/{word_id}", json=payload)

    def delete_word(self, word_id: str) -> dict[str, Any]:
        return self._request("DELETE", f"/words/{word_id}")

    def create_category(self, user_id: str, name: str) -> dict[str, Any]:
        return self._request(
            "POST",
            "/categories",
            json={"user_id": user_id, "name": name},
        )

    def list_categories(self, *, user_id: str | None = None) -> list[dict[str, Any]]:
        params = {"user_id": user_id} if user_id is not None else None
        return self._request("GET", "/categories", params=params)

    def get_category(self, category_id: str) -> dict[str, Any]:
        return self._request("GET", f"/categories/{category_id}")

    def update_category(
        self,
        category_id: str,
        *,
        user_id: str,
        name: str,
    ) -> dict[str, Any]:
        return self._request(
            "PUT",
            f"/categories/{category_id}",
            json={"user_id": user_id, "name": name},
        )

    def delete_category(self, category_id: str) -> dict[str, Any]:
        return self._request("DELETE", f"/categories/{category_id}")

    def list_translations(self, word_id: str) -> list[dict[str, Any]]:
        return self._request("GET", f"/words/{word_id}/translations")

    def create_translation(
        self,
        word_id: str,
        text: str,
        language: str,
        note: str | None = None,
    ) -> dict[str, Any]:
        payload = {"text": text, "language": language}
        if note:
            payload["note"] = note
        return self._request("POST", f"/words/{word_id}/translations", json=payload)

    def get_translation(self, translation_id: str) -> dict[str, Any]:
        return self._request("GET", f"/translations/{translation_id}")

    def update_translation(
        self,
        translation_id: str,
        *,
        word_id: str,
        text: str,
        language: str,
        note: str | None,
    ) -> dict[str, Any]:
        payload = {
            "word_id": word_id,
            "text": text,
            "language": language,
            "note": note,
        }
        return self._request("PUT", f"/translations/{translation_id}", json=payload)

    def delete_translation(self, translation_id: str) -> dict[str, Any]:
        return self._request("DELETE", f"/translations/{translation_id}")

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        """Send a request and normalize API errors into readable exceptions."""
        try:
            response = self.session.request(
                method,
                f"{self.base_url}{path}",
                timeout=10,
                **kwargs,
            )
        except requests.RequestException as exc:
            raise ApiError(0, f"Could not reach API: {exc}") from exc

        try:
            payload = response.json()
        except ValueError:
            payload = response.text

        if not response.ok:
            if isinstance(payload, dict):
                message = payload.get("error") or payload.get("message") or str(payload)
            else:
                message = str(payload)
            raise ApiError(response.status_code, f"{response.status_code}: {message}")

        return payload
