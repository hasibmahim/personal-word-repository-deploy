"""Auxiliary study-pack service powered by the main word repository API."""

from __future__ import annotations

import os
import random
from typing import Any

import requests
from flask import Flask, current_app, jsonify, request


DEFAULT_MAIN_API_BASE_URL = os.getenv("MAIN_API_BASE_URL", "http://127.0.0.1:5000")


class MainApiError(RuntimeError):
    """Raised when the auxiliary service cannot read from the main API."""


class MainApiClient:
    """Small HTTP client for the Personal Word Repository API."""

    def __init__(self, base_url: str, session: requests.Session | None = None):
        self.base_url = base_url.rstrip("/")
        self.session = session or requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def list_words(
        self,
        user_id: str,
        *,
        category_id: str | None = None,
    ) -> list[dict[str, Any]]:
        params = {"user_id": user_id}
        if category_id:
            params["category_id"] = category_id
        return self._request("GET", "/words", params=params)

    def list_categories(self, user_id: str) -> list[dict[str, Any]]:
        return self._request("GET", "/categories", params={"user_id": user_id})

    def list_translations(self, word_id: str) -> list[dict[str, Any]]:
        return self._request("GET", f"/words/{word_id}/translations")

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        try:
            response = self.session.request(
                method,
                f"{self.base_url}{path}",
                timeout=10,
                **kwargs,
            )
        except requests.RequestException as exc:
            raise MainApiError(f"could not reach main API: {exc}") from exc

        try:
            payload = response.json()
        except ValueError:
            payload = response.text

        if not response.ok:
            if isinstance(payload, dict):
                message = payload.get("error") or payload.get("message") or str(payload)
            else:
                message = str(payload)
            raise MainApiError(f"main API returned {response.status_code}: {message}")

        return payload


class StudyPackService:
    """Build derived study-pack responses from live main API data."""

    def __init__(self, api_client: MainApiClient, rng: random.Random | None = None):
        self.api_client = api_client
        self.rng = rng or random.Random()

    def random_pack(self, user_id: str, count: int) -> dict[str, Any]:
        items = self._load_words_with_translations(user_id)
        chosen_items = self.rng.sample(items, k=min(count, len(items))) if items else []
        return {
            "type": "random",
            "user_id": user_id,
            "count": len(chosen_items),
            "requested_count": count,
            "source_api": self.api_client.base_url,
            "items": chosen_items,
        }

    def missing_translations_pack(self, user_id: str) -> dict[str, Any]:
        items = [
            item
            for item in self._load_words_with_translations(user_id)
            if not item["translations"]
        ]
        return {
            "type": "missing_translations",
            "user_id": user_id,
            "count": len(items),
            "source_api": self.api_client.base_url,
            "items": items,
        }

    def category_pack(self, user_id: str, category_id: str) -> dict[str, Any]:
        categories = {
            category["id"]: category
            for category in self.api_client.list_categories(user_id)
        }
        items = self._load_words_with_translations(user_id, category_id=category_id)
        return {
            "type": "by_category",
            "user_id": user_id,
            "category_id": category_id,
            "category_name": categories.get(category_id, {}).get("name"),
            "count": len(items),
            "source_api": self.api_client.base_url,
            "items": items,
        }

    def _load_words_with_translations(
        self,
        user_id: str,
        *,
        category_id: str | None = None,
    ) -> list[dict[str, Any]]:
        words = self.api_client.list_words(user_id, category_id=category_id)
        return [self._enrich_word(word) for word in words]

    def _enrich_word(self, word: dict[str, Any]) -> dict[str, Any]:
        return {
            **word,
            "translations": self.api_client.list_translations(word["id"]),
        }


def create_app(config: dict[str, Any] | None = None) -> Flask:
    """Create and configure the study-pack service application."""
    app = Flask(__name__)
    app.config["MAIN_API_BASE_URL"] = DEFAULT_MAIN_API_BASE_URL

    if config:
        app.config.update(config)

    app.config.setdefault(
        "STUDY_PACK_SERVICE",
        StudyPackService(MainApiClient(app.config["MAIN_API_BASE_URL"])),
    )

    @app.get("/healthz")
    def healthz() -> tuple[dict[str, str], int]:
        return {"status": "ok"}, 200

    @app.get("/study-pack/random")
    def random_study_pack() -> tuple[Any, int]:
        user_id = request.args.get("user_id")
        count = request.args.get("count", default="5")

        if not user_id:
            return jsonify({"error": "user_id is required"}), 400

        try:
            count_value = int(count)
        except ValueError:
            return jsonify({"error": "count must be an integer"}), 400

        if count_value <= 0:
            return jsonify({"error": "count must be greater than zero"}), 400

        return _serve_pack(lambda service: service.random_pack(user_id, count_value))

    @app.get("/study-pack/missing-translations")
    def missing_translations_pack() -> tuple[Any, int]:
        user_id = request.args.get("user_id")
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400

        return _serve_pack(lambda service: service.missing_translations_pack(user_id))

    @app.get("/study-pack/by-category")
    def category_study_pack() -> tuple[Any, int]:
        user_id = request.args.get("user_id")
        category_id = request.args.get("category_id")

        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        if not category_id:
            return jsonify({"error": "category_id is required"}), 400

        return _serve_pack(lambda service: service.category_pack(user_id, category_id))

    return app


def _serve_pack(builder) -> tuple[Any, int]:
    """Build a response or map upstream failures into a 502 payload."""
    service = current_app.config["STUDY_PACK_SERVICE"]
    try:
        payload = builder(service)
    except MainApiError as error:
        return (
            jsonify(
                {
                    "error": str(error),
                    "source_api": current_app.config["MAIN_API_BASE_URL"],
                }
            ),
            502,
        )
    return jsonify(payload), 200


app = create_app()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5050"))
    app.run(host="0.0.0.0", port=port, debug=True)
