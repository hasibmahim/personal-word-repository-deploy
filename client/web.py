"""Flask GUI client for the Personal Word Repository API."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from flask import (
    Flask,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

try:
    from .api_client import ApiError, WordRepositoryApiClient
    from .main import DEFAULT_API_BASE_URL, DEFAULT_AUX_SERVICE_BASE_URL, DEFAULT_STATE_PATH
    from .storage import ClientState, StateStore
    from .study_pack_client import StudyPackClient, StudyPackError
except ImportError:
    from api_client import ApiError, WordRepositoryApiClient
    from main import DEFAULT_API_BASE_URL, DEFAULT_AUX_SERVICE_BASE_URL, DEFAULT_STATE_PATH
    from storage import ClientState, StateStore
    from study_pack_client import StudyPackClient, StudyPackError


def create_web_app(
    api_base_url: str = DEFAULT_API_BASE_URL,
    aux_service_base_url: str = DEFAULT_AUX_SERVICE_BASE_URL,
    state_path: Path = DEFAULT_STATE_PATH,
    *,
    api_client: WordRepositoryApiClient | None = None,
    study_pack_client: StudyPackClient | None = None,
    state_store: StateStore | None = None,
) -> Flask:
    """Create the browser-based GUI client."""
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.secret_key = os.getenv("WORDREPO_CLIENT_SECRET", "wordrepo-gui-dev-secret")

    app.extensions["wordrepo_api_client"] = api_client or WordRepositoryApiClient(
        api_base_url
    )
    app.extensions["wordrepo_study_pack_client"] = (
        study_pack_client or StudyPackClient(aux_service_base_url)
    )
    app.extensions["wordrepo_state_store"] = state_store or StateStore(state_path)

    @app.context_processor
    def inject_layout_context() -> dict[str, Any]:
        active_user = get_active_user()
        return {
            "active_user": active_user,
            "api_base_url": app.extensions["wordrepo_api_client"].base_url,
            "aux_service_base_url": app.extensions[
                "wordrepo_study_pack_client"
            ].base_url,
        }

    @app.get("/")
    def dashboard():
        active_user = get_active_user()
        health = get_api_health()
        words = []
        categories = []
        translation_count = 0
        study_summary = None
        study_error = None

        if active_user:
            words = list_words_for_user(active_user["id"])
            categories = list_categories_for_user(active_user["id"])
            translation_count = sum(
                len(list_translations_for_word(word["id"])) for word in words
            )
            try:
                study_summary = study_client().missing_translations_pack(active_user["id"])
            except StudyPackError as error:
                study_error = str(error)

        return render_template(
            "dashboard.html",
            health=health,
            words=words[:5],
            categories=categories[:5],
            translation_count=translation_count,
            study_summary=study_summary,
            study_error=study_error,
        )

    @app.get("/users")
    def users():
        return render_template("users.html", users=load_state().users)

    @app.post("/users")
    def create_user():
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        if not email or not password:
            flash("Email and password are required.", "error")
            return redirect(url_for("users"))

        try:
            user = api_client_from_app().create_user(email, password)
        except ApiError as error:
            flash(f"Could not create user: {error}", "error")
            return redirect(url_for("users"))

        state = load_state()
        state.users = upsert_user(state.users, user)
        state.active_user_id = user["id"]
        save_state(state)
        flash(f"Created and activated {user['email']}.", "success")
        return redirect(url_for("dashboard"))

    @app.post("/users/<user_id>/activate")
    def activate_user(user_id: str):
        state = load_state()
        user = next((item for item in state.users if item["id"] == user_id), None)
        if not user:
            flash("Selected user is not saved locally.", "error")
            return redirect(url_for("users"))

        state.active_user_id = user_id
        save_state(state)
        flash(f"Activated {user['email']}.", "success")
        return redirect(url_for("dashboard"))

    @app.get("/words")
    def words():
        active_user = require_active_user("Create or activate a user first.")
        if active_user is None:
            return redirect(url_for("users"))

        parts_of_speech = safe_list_parts_of_speech()
        categories = list_categories_for_user(active_user["id"])
        words_for_user = list_words_for_user(active_user["id"])
        return render_template(
            "words.html",
            words=words_for_user,
            parts_of_speech=parts_of_speech,
            categories=categories,
        )

    @app.post("/words")
    def create_word():
        active_user = require_active_user("Create or activate a user first.")
        if active_user is None:
            return redirect(url_for("users"))

        category_ids = [value for value in request.form.getlist("category_ids") if value]
        try:
            api_client_from_app().create_word(
                active_user["id"],
                request.form.get("text", "").strip(),
                request.form.get("language", "").strip(),
                int(request.form.get("part_of_speech_id", "0")),
                category_ids=category_ids,
            )
        except (ValueError, ApiError) as error:
            flash(f"Could not create word: {error}", "error")
            return redirect(url_for("words"))

        flash("Word created.", "success")
        return redirect(url_for("words"))

    @app.get("/words/<word_id>")
    def word_detail(word_id: str):
        active_user = require_active_user("Create or activate a user first.")
        if active_user is None:
            return redirect(url_for("users"))

        try:
            word = api_client_from_app().get_word(word_id)
        except ApiError as error:
            flash(f"Could not load word: {error}", "error")
            return redirect(url_for("words"))

        categories = list_categories_for_user(active_user["id"])
        translations = list_translations_for_word(word_id)
        return render_template(
            "word_detail.html",
            word=word,
            categories=categories,
            parts_of_speech=safe_list_parts_of_speech(),
            translations=translations,
        )

    @app.post("/words/<word_id>/update")
    def update_word(word_id: str):
        category_ids = [value for value in request.form.getlist("category_ids") if value]
        try:
            api_client_from_app().update_word(
                word_id,
                text=request.form.get("text", "").strip() or None,
                language=request.form.get("language", "").strip() or None,
                part_of_speech_id=int(request.form["part_of_speech_id"]),
                category_ids=category_ids,
            )
        except (KeyError, ValueError, ApiError) as error:
            flash(f"Could not update word: {error}", "error")
            return redirect(url_for("word_detail", word_id=word_id))

        flash("Word updated.", "success")
        return redirect(url_for("word_detail", word_id=word_id))

    @app.post("/words/<word_id>/delete")
    def delete_word(word_id: str):
        try:
            api_client_from_app().delete_word(word_id)
        except ApiError as error:
            flash(f"Could not delete word: {error}", "error")
            return redirect(url_for("word_detail", word_id=word_id))

        flash("Word deleted.", "success")
        return redirect(url_for("words"))

    @app.get("/categories")
    def categories():
        active_user = require_active_user("Create or activate a user first.")
        if active_user is None:
            return redirect(url_for("users"))

        return render_template(
            "categories.html",
            categories=list_categories_for_user(active_user["id"]),
        )

    @app.post("/categories")
    def create_category():
        active_user = require_active_user("Create or activate a user first.")
        if active_user is None:
            return redirect(url_for("users"))

        try:
            api_client_from_app().create_category(
                active_user["id"],
                request.form.get("name", "").strip(),
            )
        except ApiError as error:
            flash(f"Could not create category: {error}", "error")
            return redirect(url_for("categories"))

        flash("Category created.", "success")
        return redirect(url_for("categories"))

    @app.post("/categories/<category_id>/update")
    def update_category(category_id: str):
        try:
            api_client_from_app().update_category(
                category_id, request.form.get("name", "").strip()
            )
        except ApiError as error:
            flash(f"Could not update category: {error}", "error")
            return redirect(url_for("categories"))

        flash("Category updated.", "success")
        return redirect(url_for("categories"))

    @app.post("/categories/<category_id>/delete")
    def delete_category(category_id: str):
        try:
            api_client_from_app().delete_category(category_id)
        except ApiError as error:
            flash(f"Could not delete category: {error}", "error")
            return redirect(url_for("categories"))

        flash("Category deleted.", "success")
        return redirect(url_for("categories"))

    @app.post("/words/<word_id>/translations")
    def create_translation(word_id: str):
        try:
            api_client_from_app().create_translation(
                word_id,
                request.form.get("text", "").strip(),
                request.form.get("language", "").strip(),
                note=request.form.get("note", "").strip() or None,
            )
        except ApiError as error:
            flash(f"Could not create translation: {error}", "error")
            return redirect(url_for("word_detail", word_id=word_id))

        flash("Translation created.", "success")
        return redirect(url_for("word_detail", word_id=word_id))

    @app.post("/translations/<translation_id>/update")
    def update_translation(translation_id: str):
        word_id = request.form.get("word_id", "").strip()
        try:
            api_client_from_app().update_translation(
                translation_id,
                text=request.form.get("text", "").strip() or None,
                language=request.form.get("language", "").strip() or None,
                note=request.form.get("note", "").strip() or None,
            )
        except ApiError as error:
            flash(f"Could not update translation: {error}", "error")
            return redirect(url_for("word_detail", word_id=word_id))

        flash("Translation updated.", "success")
        return redirect(url_for("word_detail", word_id=word_id))

    @app.post("/translations/<translation_id>/delete")
    def delete_translation(translation_id: str):
        word_id = request.form.get("word_id", "").strip()
        try:
            api_client_from_app().delete_translation(translation_id)
        except ApiError as error:
            flash(f"Could not delete translation: {error}", "error")
            return redirect(url_for("word_detail", word_id=word_id))

        flash("Translation deleted.", "success")
        return redirect(url_for("word_detail", word_id=word_id))

    @app.get("/study-packs")
    def study_packs():
        active_user = require_active_user("Create or activate a user first.")
        if active_user is None:
            return redirect(url_for("users"))

        return render_template(
            "study_packs.html",
            categories=list_categories_for_user(active_user["id"]),
            random_pack=None,
            missing_pack=None,
            category_pack=None,
            study_error=None,
        )

    @app.post("/study-packs")
    def load_study_packs():
        active_user = require_active_user("Create or activate a user first.")
        if active_user is None:
            return redirect(url_for("users"))

        action = request.form.get("action", "random")
        categories = list_categories_for_user(active_user["id"])
        random_pack = None
        missing_pack = None
        category_pack = None
        study_error = None

        try:
            if action == "random":
                count = int(request.form.get("count", "5"))
                random_pack = study_client().random_pack(active_user["id"], count)
            elif action == "missing":
                missing_pack = study_client().missing_translations_pack(active_user["id"])
            elif action == "category":
                category_id = request.form.get("category_id", "").strip()
                category_pack = study_client().category_pack(active_user["id"], category_id)
        except (ValueError, StudyPackError) as error:
            study_error = str(error)

        return render_template(
            "study_packs.html",
            categories=categories,
            random_pack=random_pack,
            missing_pack=missing_pack,
            category_pack=category_pack,
            study_error=study_error,
        )

    return app


def api_client_from_app() -> WordRepositoryApiClient:
    """Return the configured API client instance."""
    return current_app.extensions["wordrepo_api_client"]


def study_client() -> StudyPackClient:
    """Return the configured study-pack client instance."""
    return current_app.extensions["wordrepo_study_pack_client"]


def state_store() -> StateStore:
    """Return the configured state store."""
    return current_app.extensions["wordrepo_state_store"]


def load_state() -> ClientState:
    """Load the locally saved GUI state."""
    return state_store().load()


def save_state(state: ClientState) -> None:
    """Persist GUI state back to disk."""
    state_store().save(state)


def upsert_user(users: list[dict[str, str]], next_user: dict[str, str]) -> list[dict[str, str]]:
    """Insert or replace a saved user and keep the list sorted by email."""
    remaining = [user for user in users if user["id"] != next_user["id"]]
    remaining.append(next_user)
    return sorted(remaining, key=lambda user: user["email"].lower())


def get_active_user() -> dict[str, str] | None:
    """Return the active saved user, if one is available."""
    state = load_state()
    if not state.active_user_id:
        return None

    user = next(
        (item for item in state.users if item["id"] == state.active_user_id),
        None,
    )
    if user:
        return user

    state.active_user_id = None
    save_state(state)
    return None


def require_active_user(message: str) -> dict[str, str] | None:
    """Return the active user or flash a message when missing."""
    active_user = get_active_user()
    if active_user is None:
        flash(message, "error")
    return active_user


def get_api_health() -> dict[str, str]:
    """Return API health information without raising into the template."""
    try:
        payload = api_client_from_app().healthz()
        return {"status": payload["status"], "detail": "API reachable"}
    except ApiError as error:
        return {"status": "offline", "detail": str(error)}


def safe_list_parts_of_speech() -> list[dict[str, Any]]:
    """Return parts of speech or an empty list when unavailable."""
    try:
        return api_client_from_app().list_parts_of_speech()
    except ApiError as error:
        flash(f"Could not load parts of speech: {error}", "error")
        return []


def list_words_for_user(user_id: str) -> list[dict[str, Any]]:
    """Fetch all words for a user and persist the seen IDs locally."""
    words = api_client_from_app().list_words(user_id=user_id)
    state = load_state()
    state.word_ids_by_user[user_id] = [word["id"] for word in words]
    save_state(state)
    return words


def list_categories_for_user(user_id: str) -> list[dict[str, Any]]:
    """Fetch all categories for a user and persist the seen IDs locally."""
    categories = api_client_from_app().list_categories(user_id=user_id)
    state = load_state()
    state.category_ids_by_user[user_id] = [category["id"] for category in categories]
    save_state(state)
    return categories


def list_translations_for_word(word_id: str) -> list[dict[str, Any]]:
    """Fetch translations for a word while surfacing readable errors."""
    try:
        return api_client_from_app().list_translations(word_id)
    except ApiError as error:
        flash(f"Could not load translations: {error}", "error")
        return []


if __name__ == "__main__":
    app = create_web_app()
    app.run(debug=True, port=int(os.getenv("WORDREPO_CLIENT_PORT", "8001")))
