"""Tests for terminal-client helper modules."""

from pathlib import Path

from client.api_client import WordRepositoryApiClient
from client.main import upsert_user
from client.storage import ClientState, StateStore
from client.study_pack_client import StudyPackClient, StudyPackError


class DummyResponse:
    """Minimal fake HTTP response for client-wrapper tests."""

    def __init__(self, *, ok, payload, status_code=200):
        self.ok = ok
        self._payload = payload
        self.status_code = status_code
        self.text = str(payload)

    def json(self):
        return self._payload


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
