"""Tests for the Deadline 5 auxiliary study-pack service."""

from auxiliary_service.app import MainApiError, StudyPackService, create_app


class FakeMainApiClient:
    """In-memory fake main API client for study-pack tests."""

    def __init__(self):
        self.base_url = "http://fake-main-api"
        self.words = {
            "user-1": [
                {
                    "id": "word-1",
                    "user_id": "user-1",
                    "text": "run",
                    "language": "en",
                    "part_of_speech_id": 2,
                    "categories": ["cat-1"],
                },
                {
                    "id": "word-2",
                    "user_id": "user-1",
                    "text": "cat",
                    "language": "en",
                    "part_of_speech_id": 1,
                    "categories": ["cat-2"],
                },
            ]
        }
        self.categories = {
            "user-1": [
                {"id": "cat-1", "user_id": "user-1", "name": "verbs", "words": ["word-1"]},
                {"id": "cat-2", "user_id": "user-1", "name": "animals", "words": ["word-2"]},
            ]
        }
        self.translations = {
            "word-1": [{"id": "tr-1", "word_id": "word-1", "text": "juosta", "language": "fi"}],
            "word-2": [],
        }

    def list_words(self, user_id, *, category_id=None):
        items = list(self.words.get(user_id, []))
        if category_id:
            items = [item for item in items if category_id in item["categories"]]
        return items

    def list_categories(self, user_id):
        return list(self.categories.get(user_id, []))

    def list_translations(self, word_id):
        return list(self.translations.get(word_id, []))


class FakeStudyPackService:
    """Small stub for route-level tests."""

    def random_pack(self, user_id, count):
        if user_id == "fail":
            raise MainApiError("upstream failed")
        return {"type": "random", "user_id": user_id, "count": count, "items": []}

    def missing_translations_pack(self, user_id):
        return {"type": "missing_translations", "user_id": user_id, "count": 0, "items": []}

    def category_pack(self, user_id, category_id):
        return {
            "type": "by_category",
            "user_id": user_id,
            "category_id": category_id,
            "count": 0,
            "items": [],
        }

    def quiz_pack(self, user_id, *, count, category_id=None):
        return {
            "type": "quiz",
            "user_id": user_id,
            "category_id": category_id,
            "count": count,
            "questions": [],
        }


def test_study_pack_service_builds_random_pack_from_live_words():
    service = StudyPackService(FakeMainApiClient())

    payload = service.random_pack("user-1", 5)

    assert payload["type"] == "random"
    assert payload["count"] == 2
    assert {item["id"] for item in payload["items"]} == {"word-1", "word-2"}
    assert payload["items"][0]["translations"] is not None


def test_study_pack_service_filters_words_missing_translations():
    service = StudyPackService(FakeMainApiClient())

    payload = service.missing_translations_pack("user-1")

    assert payload["type"] == "missing_translations"
    assert payload["count"] == 1
    assert payload["items"][0]["id"] == "word-2"


def test_study_pack_service_filters_words_by_category():
    service = StudyPackService(FakeMainApiClient())

    payload = service.category_pack("user-1", "cat-1")

    assert payload["type"] == "by_category"
    assert payload["category_name"] == "verbs"
    assert [item["id"] for item in payload["items"]] == ["word-1"]


def test_study_pack_service_builds_quiz_questions():
    service = StudyPackService(FakeMainApiClient())

    payload = service.quiz_pack("user-1", count=5)

    assert payload["type"] == "quiz"
    assert payload["count"] == 1
    assert payload["questions"][0]["prompt"] == "run"
    assert payload["questions"][0]["accepted_answers"] == ["juosta"]
    assert "juosta" in payload["questions"][0]["choices"]


def test_auxiliary_healthz_returns_ok():
    app = create_app()
    client = app.test_client()

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_random_study_pack_requires_user_id():
    app = create_app({"STUDY_PACK_SERVICE": FakeStudyPackService()})
    client = app.test_client()

    response = client.get("/study-pack/random")

    assert response.status_code == 400
    assert response.get_json()["error"] == "user_id is required"


def test_random_study_pack_rejects_non_positive_count():
    app = create_app({"STUDY_PACK_SERVICE": FakeStudyPackService()})
    client = app.test_client()

    response = client.get("/study-pack/random?user_id=tester&count=0")

    assert response.status_code == 400
    assert response.get_json()["error"] == "count must be greater than zero"


def test_category_study_pack_requires_category_id():
    app = create_app({"STUDY_PACK_SERVICE": FakeStudyPackService()})
    client = app.test_client()

    response = client.get("/study-pack/by-category?user_id=tester")

    assert response.status_code == 400
    assert response.get_json()["error"] == "category_id is required"


def test_auxiliary_routes_return_upstream_error_as_502():
    app = create_app(
        {
            "MAIN_API_BASE_URL": "http://fake-main-api",
            "STUDY_PACK_SERVICE": FakeStudyPackService(),
        }
    )
    client = app.test_client()

    response = client.get("/study-pack/random?user_id=fail&count=1")

    assert response.status_code == 502
    assert response.get_json()["error"] == "upstream failed"


def test_quiz_study_pack_requires_user_id():
    app = create_app({"STUDY_PACK_SERVICE": FakeStudyPackService()})
    client = app.test_client()

    response = client.get("/study-pack/quiz")

    assert response.status_code == 400
    assert response.get_json()["error"] == "user_id is required"


def test_quiz_study_pack_rejects_non_positive_count():
    app = create_app({"STUDY_PACK_SERVICE": FakeStudyPackService()})
    client = app.test_client()

    response = client.get("/study-pack/quiz?user_id=tester&count=0")

    assert response.status_code == 400
    assert response.get_json()["error"] == "count must be greater than zero"
