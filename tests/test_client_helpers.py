"""Tests for terminal-client helper modules."""

import json
from pathlib import Path

from client.api_client import WordRepositoryApiClient
from client.main import upsert_user
from client.storage import ClientState, StateStore
from client.study_pack_client import StudyPackClient, StudyPackError
from client.web import create_web_app


class DummyResponse:
    """Minimal fake HTTP response for client-wrapper tests."""

    def __init__(self, *, ok, payload, status_code=200):
        self.ok = ok
        self._payload = payload
        self.status_code = status_code
        self.text = str(payload)

    def json(self):
        return self._payload


class FakeApiClient:
    """Minimal in-memory API double for GUI tests."""

    def __init__(self):
        self.users = []
        self.parts_of_speech = [{"id": 1, "code": "noun", "name": "Noun"}]
        self.categories = {}
        self.words = {}
        self.translations = {}

    @property
    def base_url(self):
        return "http://api.test"

    def healthz(self):
        return {"status": "ok"}

    def create_user(self, email, password):
        user = {"id": f"user-{len(self.users) + 1}", "email": email}
        self.users.append(user)
        self.categories[user["id"]] = []
        self.words[user["id"]] = []
        return user

    def list_parts_of_speech(self):
        return self.parts_of_speech

    def create_category(self, user_id, name):
        category = {"id": f"cat-{len(self.categories[user_id]) + 1}", "name": name, "user_id": user_id, "words": []}
        self.categories[user_id].append(category)
        return category

    def list_categories(self, user_id=None):
        return list(self.categories.get(user_id, []))

    def create_word(self, user_id, text, language, part_of_speech_id, category_ids=None):
        word = {
            "id": f"word-{len(self.words[user_id]) + 1}",
            "user_id": user_id,
            "text": text,
            "language": language,
            "part_of_speech_id": part_of_speech_id,
            "categories": category_ids or [],
        }
        self.words[user_id].append(word)
        self.translations[word["id"]] = []
        return word

    def list_words(self, user_id=None, category_id=None):
        payload = list(self.words.get(user_id, []))
        if category_id is not None:
            payload = [word for word in payload if category_id in word["categories"]]
        return payload

    def get_word(self, word_id):
        for words in self.words.values():
            for word in words:
                if word["id"] == word_id:
                    return word
        raise AssertionError("word not found in fake client")

    def list_translations(self, word_id):
        return list(self.translations.get(word_id, []))

    def create_translation(self, word_id, text, language, note=None):
        translation = {
            "id": f"translation-{len(self.translations[word_id]) + 1}",
            "word_id": word_id,
            "text": text,
            "language": language,
            "note": note,
        }
        self.translations[word_id].append(translation)
        return translation


class FakeStudyPackClient:
    """Minimal study-pack double for GUI tests."""

    @property
    def base_url(self):
        return "http://study.test"

    def missing_translations_pack(self, user_id):
        return {"count": 1, "items": [{"text": "bonjour", "language": "fr"}]}

    def random_pack(self, user_id, count=5):
        return {"count": count, "items": [{"text": "salut", "language": "fr"}]}

    def category_pack(self, user_id, category_id):
        return {"count": 1, "items": [{"text": "train", "language": "fr"}]}

    def quiz_pack(self, user_id, *, count=5, category_id=None):
        return {
            "count": count,
            "questions": [
                {
                    "question_id": 1,
                    "prompt": "bonjour",
                    "prompt_language": "fr",
                    "accepted_answers": ["hello"],
                    "choices": ["hello", "cat"],
                }
            ],
        }


def test_state_store_round_trip(tmp_path: Path):
    store = StateStore(tmp_path / "client_state.json")
    state = ClientState(
        users=[{"id": "user-1", "email": "learner@example.com"}],
        active_user_id="user-1",
        active_word_id="word-1",
        word_ids_by_user={"user-1": ["word-1"]},
        category_ids_by_user={"user-1": ["cat-1"]},
    )

    store.save(state)
    loaded = store.load()

    assert loaded == state


def test_upsert_user_replaces_existing_user_and_sorts_by_email():
    users = [
        {"id": "2", "email": "zoe@example.com"},
        {"id": "1", "email": "amy@example.com"},
    ]

    result = upsert_user(users, {"id": "2", "email": "bob@example.com"})

    assert result == [
        {"id": "1", "email": "amy@example.com"},
        {"id": "2", "email": "bob@example.com"},
    ]


def test_api_client_list_words_sends_query_filters(monkeypatch):
    client = WordRepositoryApiClient("http://example.test")
    captured = {}

    def fake_request(method, url, timeout, **kwargs):
        captured["method"] = method
        captured["url"] = url
        captured["params"] = kwargs.get("params")
        return DummyResponse(ok=True, payload=[{"id": "word-1"}])

    monkeypatch.setattr(client.session, "request", fake_request)

    payload = client.list_words(user_id="user-1", category_id="cat-1")

    assert payload == [{"id": "word-1"}]
    assert captured == {
        "method": "GET",
        "url": "http://example.test/words",
        "params": {"user_id": "user-1", "category_id": "cat-1"},
    }


def test_study_pack_client_raises_readable_error_for_http_failure(monkeypatch):
    client = StudyPackClient("http://study-pack.test")

    def fake_request(method, url, timeout, **kwargs):
        return DummyResponse(
            ok=False,
            payload={"error": "main API returned 502: upstream failed"},
            status_code=502,
        )

    monkeypatch.setattr(client.session, "request", fake_request)

    try:
        client.random_pack("user-1", count=2)
    except StudyPackError as error:
        assert error.status_code == 502
        assert str(error) == "502: main API returned 502: upstream failed"
    else:
        raise AssertionError("StudyPackError was not raised")


def test_gui_create_user_saves_and_activates_user(tmp_path: Path):
    app = create_web_app(
        api_client=FakeApiClient(),
        study_pack_client=FakeStudyPackClient(),
        state_store=StateStore(tmp_path / "gui_state.json"),
    )

    response = app.test_client().post(
        "/users",
        data={"email": "learner@example.com", "password": "secret123"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Created and activated learner@example.com.".encode() in response.data
    state = app.extensions["wordrepo_state_store"].load()
    assert state.active_user_id == "user-1"
    assert state.users == [{"id": "user-1", "email": "learner@example.com"}]


def test_gui_words_page_lists_active_user_vocabulary(tmp_path: Path):
    api_client = FakeApiClient()
    user = api_client.create_user("learner@example.com", "secret123")
    category = api_client.create_category(user["id"], "Travel")
    api_client.create_word(
        user["id"],
        "bonjour",
        "fr",
        1,
        category_ids=[category["id"]],
    )
    store = StateStore(tmp_path / "gui_state.json")
    store.save(ClientState(users=[user], active_user_id=user["id"]))
    app = create_web_app(
        api_client=api_client,
        study_pack_client=FakeStudyPackClient(),
        state_store=store,
    )

    response = app.test_client().get("/words")

    assert response.status_code == 200
    assert b"bonjour" in response.data
    assert b"Travel" in response.data


def test_gui_study_packs_page_renders_random_pack(tmp_path: Path):
    api_client = FakeApiClient()
    user = api_client.create_user("learner@example.com", "secret123")
    store = StateStore(tmp_path / "gui_state.json")
    store.save(ClientState(users=[user], active_user_id=user["id"]))
    app = create_web_app(
        api_client=api_client,
        study_pack_client=FakeStudyPackClient(),
        state_store=store,
    )

    response = app.test_client().post(
        "/study-packs",
        data={"action": "random", "count": "3"},
    )

    assert response.status_code == 200
    assert b"salut" in response.data
    assert b"3 item(s)" in response.data


def test_gui_study_packs_page_renders_quiz_pack(tmp_path: Path):
    api_client = FakeApiClient()
    user = api_client.create_user("learner@example.com", "secret123")
    store = StateStore(tmp_path / "gui_state.json")
    store.save(ClientState(users=[user], active_user_id=user["id"]))
    app = create_web_app(
        api_client=api_client,
        study_pack_client=FakeStudyPackClient(),
        state_store=store,
    )

    response = app.test_client().post(
        "/study-packs",
        data={"action": "quiz", "count": "4", "category_id": ""},
    )

    assert response.status_code == 200
    assert b"bonjour" in response.data
    assert b"hello" in response.data
    assert b"Accepted answer" not in response.data
    assert b"Check answers" in response.data


def test_gui_study_packs_page_scores_quiz_answers(tmp_path: Path):
    api_client = FakeApiClient()
    user = api_client.create_user("learner@example.com", "secret123")
    store = StateStore(tmp_path / "gui_state.json")
    store.save(ClientState(users=[user], active_user_id=user["id"]))
    app = create_web_app(
        api_client=api_client,
        study_pack_client=FakeStudyPackClient(),
        state_store=store,
    )

    quiz_payload = {
        "count": 1,
        "questions": [
            {
                "question_id": 1,
                "prompt": "bonjour",
                "prompt_language": "fr",
                "accepted_answers": ["hello"],
                "choices": ["hello", "cat"],
            }
        ],
    }

    response = app.test_client().post(
        "/study-packs",
        data={
            "action": "quiz-score",
            "quiz_payload": json.dumps(quiz_payload),
            "answer_1": "cat",
        },
    )

    assert response.status_code == 200
    assert b"Score: 0 / 1" in response.data
    assert b"Your answer: cat." in response.data
    assert b"Correct answer:" in response.data
    assert b"hello." in response.data
    assert b"Accepted answer" not in response.data
