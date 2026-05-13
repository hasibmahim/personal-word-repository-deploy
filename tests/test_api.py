"""Functional tests for the REST API."""
import uuid


API_KEY_HEADER = {"Authorization": "Bearer API_KEY_12345"}


def create_user(client, email=None, password="secret123"):
    """Create a user and return the JSON response body."""
    response = client.post(
        "/users",
        json={
            "email": email or f"{uuid.uuid4()}@example.com",
            "password": password,
        },
    )
    assert response.status_code == 201
    return response.json


def create_part_of_speech(client, code="noun", name="noun"):
    """Create a part of speech and return the JSON response body."""
    response = client.post("/parts-of-speech", json={"code": code, "name": name})
    assert response.status_code == 201
    return response.json


def create_word(client, user_id, part_of_speech_id, text="run", language="en"):
    """Create a word and return the JSON response body."""
    response = client.post(
        "/words",
        json={
            "text": text,
            "language": language,
            "user_id": user_id,
            "part_of_speech_id": part_of_speech_id,
        },
    )
    assert response.status_code == 201
    return response.json


def create_category(client, user_id, name="animals"):
    """Create a category and return the JSON response body."""
    response = client.post("/categories", json={"name": name, "user_id": user_id})
    assert response.status_code == 201
    return response.json


def create_translation(client, word_id, text="juosta", language="fi", note=None):
    """Create a translation and return the JSON response body."""
    payload = {"text": text, "language": language}
    if note is not None:
        payload["note"] = note
    response = client.post(f"/words/{word_id}/translations", json=payload)
    assert response.status_code == 201
    return response.json


def test_healthz_returns_ok(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json == {"status": "ok"}


def test_openapi_spec_is_served(client):
    response = client.get("/openapi.yaml")
    assert response.status_code == 200
    assert "openapi: 3.0.3" in response.get_data(as_text=True)


def test_docs_is_served(client):
    response = client.get("/docs")
    assert response.status_code == 200
    assert "SwaggerUIBundle" in response.get_data(as_text=True)


def test_get_users_requires_auth(client):
    response = client.get("/users")
    assert response.status_code == 401


def test_get_users_returns_list_with_auth(client):
    create_user(client)
    response = client.get("/users", headers=API_KEY_HEADER)
    assert response.status_code == 200
    assert len(response.json) == 1


def test_create_user_success(client):
    response = client.post(
        "/users",
        json={"email": f"{uuid.uuid4()}@example.com", "password": "hashed_password"},
    )
    assert response.status_code == 201
    assert "id" in response.json


def test_create_user_invalid_email(client):
    response = client.post(
        "/users",
        json={"email": "not-an-email", "password": "secret123"},
    )
    assert response.status_code == 400
    assert response.json["error"] == "invalid request body"


def test_create_user_rejects_extra_fields(client):
    response = client.post(
        "/users",
        json={
            "email": "test@example.com",
            "password": "secret123",
            "nickname": "tester",
        },
    )
    assert response.status_code == 400


def test_create_user_duplicate_email(client):
    create_user(client, email="test@example.com")
    response = client.post(
        "/users",
        json={"email": "test@example.com", "password": "new_password"},
    )
    assert response.status_code == 409


def test_get_user_not_found(client):
    response = client.get("/users/does-not-exist")
    assert response.status_code == 404


def test_get_user_success(client):
    user = create_user(client)
    response = client.get(f"/users/{user['id']}")
    assert response.status_code == 200
    assert response.json["id"] == user["id"]


def test_update_user_duplicate_email(client):
    first_user = create_user(client, email="first@example.com")
    create_user(client, email="second@example.com")
    response = client.put(
        f"/users/{first_user['id']}",
        json={"email": "second@example.com", "password": "newsecret123"},
    )
    assert response.status_code == 409


def test_update_user_requires_body(client):
    user = create_user(client)
    response = client.put(f"/users/{user['id']}", json={})
    assert response.status_code == 400


def test_update_user_not_found(client):
    response = client.put(
        "/users/does-not-exist",
        json={"email": "updated@example.com", "password": "newsecret123"},
    )
    assert response.status_code == 404


def test_update_user_success(client):
    user = create_user(client)
    response = client.put(
        f"/users/{user['id']}",
        json={"email": "updated@example.com", "password": "newsecret123"},
    )
    assert response.status_code == 200
    assert response.json["email"] == "updated@example.com"


def test_delete_user_success(client):
    user = create_user(client)
    response = client.delete(f"/users/{user['id']}")
    assert response.status_code == 204


def test_delete_user_not_found(client):
    response = client.delete("/users/does-not-exist")
    assert response.status_code == 404


def test_create_part_of_speech_success(client):
    response = client.post("/parts-of-speech", json={"code": "noun", "name": "noun"})
    assert response.status_code == 201
    assert response.json["name"] == "noun"


def test_create_part_of_speech_rejects_invalid_body(client):
    response = client.post("/parts-of-speech", json={"code": "noun", "extra": True})
    assert response.status_code == 400


def test_create_part_of_speech_duplicate_code(client):
    create_part_of_speech(client, code="verb", name="verb")
    response = client.post("/parts-of-speech", json={"code": "verb", "name": "verb2"})
    assert response.status_code == 409


def test_parts_of_speech_get_returns_cache_headers(client):
    create_part_of_speech(client, code="noun", name="noun")
    response = client.get("/parts-of-speech")
    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "public, max-age=300"
    assert response.headers["ETag"]


def test_parts_of_speech_get_supports_304(client):
    create_part_of_speech(client, code="noun", name="noun")
    first_response = client.get("/parts-of-speech")
    second_response = client.get(
        "/parts-of-speech",
        headers={"If-None-Match": first_response.headers["ETag"]},
    )
    assert second_response.status_code == 304


def test_update_part_of_speech_success(client):
    pos = create_part_of_speech(client, code="adj", name="adjective")
    response = client.put(
        f"/parts-of-speech/{pos['id']}",
        json={"code": "adj", "name": "Adjective"},
    )
    assert response.status_code == 200
    assert response.json["name"] == "Adjective"


def test_update_part_of_speech_requires_valid_body(client):
    pos = create_part_of_speech(client, code="verb", name="verb")
    response = client.put(
        f"/parts-of-speech/{pos['id']}",
        json={"unknown": "field"},
    )
    assert response.status_code == 400


def test_update_part_of_speech_duplicate_code(client):
    create_part_of_speech(client, code="verb-existing", name="Verb Existing")
    pos = create_part_of_speech(client, code="verb-new", name="Verb New")
    response = client.put(
        f"/parts-of-speech/{pos['id']}",
        json={"code": "verb-existing", "name": "Verb New"},
    )
    assert response.status_code == 409


def test_delete_part_of_speech_not_found(client):
    response = client.delete("/parts-of-speech/999")
    assert response.status_code == 404


def test_update_part_of_speech_not_found(client):
    response = client.put("/parts-of-speech/999", json={"code": "verb", "name": "Verb"})
    assert response.status_code == 404


def test_delete_part_of_speech_success(client):
    pos = create_part_of_speech(client, code="delete-pos", name="noun")
    response = client.delete(f"/parts-of-speech/{pos['id']}")
    assert response.status_code == 204


def test_create_word_success(client):
    user = create_user(client, email="test@example.com")
    pos = create_part_of_speech(client, code="run-verb", name="verb")
    response = client.post(
        "/words",
        json={
            "text": "run",
            "language": "en",
            "user_id": user["id"],
            "part_of_speech_id": pos["id"],
        },
    )
    assert response.status_code == 201
    assert response.json["text"] == "run"


def test_create_word_rejects_extra_fields(client):
    user = create_user(client)
    pos = create_part_of_speech(client, code="word-extra", name="verb")
    response = client.post(
        "/words",
        json={
            "text": "run",
            "language": "en",
            "user_id": user["id"],
            "part_of_speech_id": pos["id"],
            "extra": True,
        },
    )
    assert response.status_code == 400


def test_create_word_missing_user(client):
    pos = create_part_of_speech(client, code="word-user", name="verb")
    response = client.post(
        "/words",
        json={
            "text": "run",
            "language": "en",
            "user_id": "missing-user",
            "part_of_speech_id": pos["id"],
        },
    )
    assert response.status_code == 404


def test_create_word_missing_part_of_speech(client):
    user = create_user(client)
    response = client.post(
        "/words",
        json={
            "text": "run",
            "language": "en",
            "user_id": user["id"],
            "part_of_speech_id": 9999,
        },
    )
    assert response.status_code == 404


def test_create_word_with_categories(client):
    user = create_user(client)
    pos = create_part_of_speech(client, code="word-cat", name="noun")
    category = create_category(client, user["id"], "animals")
    response = client.post(
        "/words",
        json={
            "text": "cat",
            "language": "en",
            "user_id": user["id"],
            "part_of_speech_id": pos["id"],
            "category_ids": [category["id"]],
        },
    )
    assert response.status_code == 201
    assert response.json["categories"] == [category["id"]]


def test_create_word_rejects_missing_category(client):
    user = create_user(client)
    pos = create_part_of_speech(client, code="word-missing-category", name="noun")
    response = client.post(
        "/words",
        json={
            "text": "cat",
            "language": "en",
            "user_id": user["id"],
            "part_of_speech_id": pos["id"],
            "category_ids": ["missing-category"],
        },
    )
    assert response.status_code == 404


def test_get_word_not_found(client):
    response = client.get("/words/does-not-exist")
    assert response.status_code == 404


def test_get_word_success(client):
    user = create_user(client)
    pos = create_part_of_speech(client, code="get-word", name="verb")
    word = create_word(client, user["id"], pos["id"])
    response = client.get(f"/words/{word['id']}")
    assert response.status_code == 200
    assert response.json["id"] == word["id"]


def test_list_words_returns_all_words(client):
    user = create_user(client)
    pos = create_part_of_speech(client, code="word-list-all", name="verb")
    create_word(client, user["id"], pos["id"], text="run")
    create_word(client, user["id"], pos["id"], text="walk")

    response = client.get("/words")

    assert response.status_code == 200
    assert len(response.json) == 2


def test_list_words_can_filter_by_user(client):
    first_user = create_user(client, email="first-words@example.com")
    second_user = create_user(client, email="second-words@example.com")
    pos = create_part_of_speech(client, code="word-list-user", name="noun")
    first_word = create_word(client, first_user["id"], pos["id"], text="cat")
    create_word(client, second_user["id"], pos["id"], text="dog")

    response = client.get(f"/words?user_id={first_user['id']}")

    assert response.status_code == 200
    assert response.json == [first_word]


def test_list_words_can_filter_by_category(client):
    user = create_user(client)
    pos = create_part_of_speech(client, code="word-list-category", name="adjective")
    animals = create_category(client, user["id"], "animals")
    colors = create_category(client, user["id"], "colors")
    animal_word = client.post(
        "/words",
        json={
            "text": "fox",
            "language": "en",
            "user_id": user["id"],
            "part_of_speech_id": pos["id"],
            "category_ids": [animals["id"]],
        },
    ).json
    client.post(
        "/words",
        json={
            "text": "blue",
            "language": "en",
            "user_id": user["id"],
            "part_of_speech_id": pos["id"],
            "category_ids": [colors["id"]],
        },
    )

    response = client.get(f"/words?category_id={animals['id']}")

    assert response.status_code == 200
    assert response.json == [animal_word]


def test_update_word_success(client):
    user = create_user(client)
    pos = create_part_of_speech(client, code="verb-a", name="verb")
    next_pos = create_part_of_speech(client, code="verb-b", name="adverb")
    word = create_word(client, user["id"], pos["id"])
    category = create_category(client, user["id"], "running")
    response = client.put(
        f"/words/{word['id']}",
        json={
            "user_id": user["id"],
            "text": "running",
            "language": "en",
            "part_of_speech_id": next_pos["id"],
            "category_ids": [category["id"]],
        },
    )
    assert response.status_code == 200
    assert response.json["text"] == "running"
    assert response.json["part_of_speech_id"] == next_pos["id"]
    assert response.json["categories"] == [category["id"]]


def test_update_word_not_found(client):
    response = client.put(
        "/words/does-not-exist",
        json={
            "user_id": "user-1",
            "text": "running",
            "language": "en",
            "part_of_speech_id": 1,
            "category_ids": [],
        },
    )
    assert response.status_code == 404


def test_update_word_replaces_categories_with_empty_list(client):
    user = create_user(client)
    pos = create_part_of_speech(client, code="verb-lang", name="verb")
    category = create_category(client, user["id"], "verbs")
    word = client.post(
        "/words",
        json={
            "text": "run",
            "language": "en",
            "user_id": user["id"],
            "part_of_speech_id": pos["id"],
            "category_ids": [category["id"]],
        },
    ).json
    response = client.put(
        f"/words/{word['id']}",
        json={
            "user_id": user["id"],
            "text": "run",
            "language": "fi",
            "part_of_speech_id": pos["id"],
            "category_ids": [],
        },
    )
    assert response.status_code == 200
    assert response.json["language"] == "fi"
    assert response.json["categories"] == []


def test_update_word_invalid_part_of_speech(client):
    user = create_user(client)
    pos = create_part_of_speech(client, code="verb-invalid-pos", name="verb")
    word = create_word(client, user["id"], pos["id"])
    response = client.put(
        f"/words/{word['id']}",
        json={
            "user_id": user["id"],
            "text": word["text"],
            "language": word["language"],
            "part_of_speech_id": 9999,
            "category_ids": [],
        },
    )
    assert response.status_code == 404


def test_update_word_rejects_missing_category(client):
    user = create_user(client)
    pos = create_part_of_speech(client, code="verb-missing-category", name="verb")
    word = create_word(client, user["id"], pos["id"])
    response = client.put(
        f"/words/{word['id']}",
        json={
            "user_id": user["id"],
            "text": word["text"],
            "language": word["language"],
            "part_of_speech_id": pos["id"],
            "category_ids": ["missing-category"],
        },
    )
    assert response.status_code == 404


def test_update_word_rejects_owner_mismatch(client):
    user = create_user(client)
    other_user = create_user(client, email="other-owner@example.com")
    pos = create_part_of_speech(client, code="verb-category-update", name="verb")
    word = create_word(client, user["id"], pos["id"])
    response = client.put(
        f"/words/{word['id']}",
        json={
            "user_id": other_user["id"],
            "text": word["text"],
            "language": word["language"],
            "part_of_speech_id": pos["id"],
            "category_ids": [],
        },
    )
    assert response.status_code == 400


def test_update_word_rejects_partial_representation(client):
    user = create_user(client)
    pos = create_part_of_speech(client, code="verb-c", name="verb")
    word = create_word(client, user["id"], pos["id"])
    response = client.put(
        f"/words/{word['id']}",
        json={"text": "running"},
    )
    assert response.status_code == 400


def test_delete_word(client):
    user = create_user(client, email="deleteword@example.com")
    pos = create_part_of_speech(client, code="adjective", name="adjective")
    word = create_word(client, user["id"], pos["id"], text="fast")
    delete_response = client.delete(f"/words/{word['id']}")
    assert delete_response.status_code == 204
    get_response = client.get(f"/words/{word['id']}")
    assert get_response.status_code == 404


def test_delete_word_not_found(client):
    response = client.delete("/words/does-not-exist")
    assert response.status_code == 404


def test_create_category_success(client):
    user = create_user(client)
    response = client.post("/categories", json={"name": "animals", "user_id": user["id"]})
    assert response.status_code == 201
    assert response.json["name"] == "animals"


def test_create_category_requires_valid_body(client):
    response = client.post("/categories", json={"user_id": "missing-name"})
    assert response.status_code == 400


def test_create_category_missing_user(client):
    response = client.post(
        "/categories",
        json={"name": "animals", "user_id": "does-not-exist"},
    )
    assert response.status_code == 404


def test_create_category_duplicate_for_same_user(client):
    user = create_user(client)
    create_category(client, user["id"], "animals")
    response = client.post("/categories", json={"name": "animals", "user_id": user["id"]})
    assert response.status_code == 409


def test_get_category_not_found(client):
    response = client.get("/categories/does-not-exist")
    assert response.status_code == 404


def test_get_category_success(client):
    user = create_user(client)
    category = create_category(client, user["id"], "animals")
    response = client.get(f"/categories/{category['id']}")
    assert response.status_code == 200
    assert response.json["id"] == category["id"]


def test_list_categories_returns_all_categories(client):
    user = create_user(client)
    create_category(client, user["id"], "animals")
    create_category(client, user["id"], "verbs")

    response = client.get("/categories")

    assert response.status_code == 200
    assert [item["name"] for item in response.json] == ["animals", "verbs"]


def test_list_categories_can_filter_by_user(client):
    first_user = create_user(client, email="first-categories@example.com")
    second_user = create_user(client, email="second-categories@example.com")
    first_category = create_category(client, first_user["id"], "animals")
    create_category(client, second_user["id"], "colors")

    response = client.get(f"/categories?user_id={first_user['id']}")

    assert response.status_code == 200
    assert response.json == [first_category]


def test_update_category_duplicate_name(client):
    user = create_user(client)
    first = create_category(client, user["id"], "animals")
    create_category(client, user["id"], "colors")
    response = client.put(
        f"/categories/{first['id']}",
        json={"user_id": user["id"], "name": "colors"},
    )
    assert response.status_code == 409


def test_update_category_not_found(client):
    response = client.put(
        "/categories/does-not-exist",
        json={"user_id": "user-1", "name": "verbs"},
    )
    assert response.status_code == 404


def test_update_category_rejects_partial_representation(client):
    user = create_user(client)
    category = create_category(client, user["id"], "animals")
    response = client.put(f"/categories/{category['id']}", json={"name": "verbs"})
    assert response.status_code == 400


def test_update_category_success(client):
    user = create_user(client)
    category = create_category(client, user["id"], "animals")
    response = client.put(
        f"/categories/{category['id']}",
        json={"user_id": user["id"], "name": "verbs"},
    )
    assert response.status_code == 200
    assert response.json["name"] == "verbs"


def test_update_category_rejects_owner_mismatch(client):
    user = create_user(client)
    other_user = create_user(client, email="other-category-owner@example.com")
    category = create_category(client, user["id"], "animals")
    response = client.put(
        f"/categories/{category['id']}",
        json={"user_id": other_user["id"], "name": "verbs"},
    )
    assert response.status_code == 400


def test_delete_category_success(client):
    user = create_user(client)
    category = create_category(client, user["id"], "verbs")
    response = client.delete(f"/categories/{category['id']}")
    assert response.status_code == 204


def test_delete_category_not_found(client):
    response = client.delete("/categories/does-not-exist")
    assert response.status_code == 404


def test_list_translations_for_missing_word(client):
    response = client.get("/words/does-not-exist/translations")
    assert response.status_code == 404


def test_list_translations_for_word(client):
    user = create_user(client)
    pos = create_part_of_speech(client, code="verb-d", name="verb")
    word = create_word(client, user["id"], pos["id"])
    create_translation(client, word["id"], text="juosta", language="fi", note="common")
    response = client.get(f"/words/{word['id']}/translations")
    assert response.status_code == 200
    assert response.json[0]["text"] == "juosta"


def test_create_translation_rejects_extra_field(client):
    user = create_user(client)
    pos = create_part_of_speech(client, code="verb-e", name="verb")
    word = create_word(client, user["id"], pos["id"])
    response = client.post(
        f"/words/{word['id']}/translations",
        json={"text": "juosta", "language": "fi", "extra": "nope"},
    )
    assert response.status_code == 400


def test_create_translation_missing_word(client):
    response = client.post(
        "/words/does-not-exist/translations",
        json={"text": "juosta", "language": "fi"},
    )
    assert response.status_code == 404


def test_get_translation_not_found(client):
    response = client.get("/translations/does-not-exist")
    assert response.status_code == 404


def test_get_translation_success(client):
    user = create_user(client)
    pos = create_part_of_speech(client, code="verb-get-translation", name="verb")
    word = create_word(client, user["id"], pos["id"])
    translation = create_translation(client, word["id"])
    response = client.get(f"/translations/{translation['id']}")
    assert response.status_code == 200
    assert response.json["id"] == translation["id"]


def test_update_translation_success(client):
    user = create_user(client)
    pos = create_part_of_speech(client, code="verb-f", name="verb")
    word = create_word(client, user["id"], pos["id"])
    translation = create_translation(client, word["id"])
    response = client.put(
        f"/translations/{translation['id']}",
        json={
            "word_id": word["id"],
            "text": "springa",
            "language": "sv",
            "note": "colloquial",
        },
    )
    assert response.status_code == 200
    assert response.json["language"] == "sv"


def test_update_translation_not_found(client):
    response = client.put(
        "/translations/does-not-exist",
        json={
            "word_id": "word-1",
            "text": "springa",
            "language": "sv",
            "note": "colloquial",
        },
    )
    assert response.status_code == 404


def test_update_translation_rejects_partial_representation(client):
    user = create_user(client)
    pos = create_part_of_speech(client, code="verb-g", name="verb")
    word = create_word(client, user["id"], pos["id"])
    translation = create_translation(client, word["id"])
    response = client.put(f"/translations/{translation['id']}", json={"text": "springa"})
    assert response.status_code == 400


def test_update_translation_rejects_word_mismatch(client):
    user = create_user(client)
    pos = create_part_of_speech(client, code="verb-g2", name="verb")
    word = create_word(client, user["id"], pos["id"])
    translation = create_translation(client, word["id"])
    response = client.put(
        f"/translations/{translation['id']}",
        json={
            "word_id": "different-word",
            "text": "springa",
            "language": "sv",
            "note": None,
        },
    )
    assert response.status_code == 400


def test_delete_translation_success(client):
    user = create_user(client)
    pos = create_part_of_speech(client, code="verb-h", name="verb")
    word = create_word(client, user["id"], pos["id"])
    translation = create_translation(client, word["id"])
    response = client.delete(f"/translations/{translation['id']}")
    assert response.status_code == 204


def test_delete_translation_not_found(client):
    response = client.delete("/translations/does-not-exist")
    assert response.status_code == 404


def test_invalid_json_body_returns_400(client):
    response = client.post(
        "/users",
        data='{"email": "broken@example.com"',
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json["error"] == "invalid JSON body"
