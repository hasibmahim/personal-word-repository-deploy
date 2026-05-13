"""JSON schema helpers for validating API request bodies."""
from jsonschema import Draft7Validator, FormatChecker


FORMAT_CHECKER = FormatChecker()

USER_CREATE_SCHEMA = {
    "type": "object",
    "required": ["email", "password"],
    "properties": {
        "email": {"type": "string", "format": "email"},
        "password": {"type": "string", "minLength": 1},
    },
    "additionalProperties": False,
}

USER_UPDATE_SCHEMA = {
    "type": "object",
    "required": ["email", "password"],
    "properties": {
        "email": {"type": "string", "format": "email"},
        "password": {"type": "string", "minLength": 1},
    },
    "additionalProperties": False,
}

WORD_CREATE_SCHEMA = {
    "type": "object",
    "required": ["text", "language", "user_id", "part_of_speech_id"],
    "properties": {
        "text": {"type": "string", "minLength": 1},
        "language": {"type": "string", "minLength": 1},
        "user_id": {"type": "string", "minLength": 1},
        "part_of_speech_id": {"type": "integer"},
        "category_ids": {
            "type": "array",
            "items": {"type": "string", "minLength": 1},
        },
    },
    "additionalProperties": False,
}

WORD_UPDATE_SCHEMA = {
    "type": "object",
    "required": ["user_id", "text", "language", "part_of_speech_id", "category_ids"],
    "properties": {
        "user_id": {"type": "string", "minLength": 1},
        "text": {"type": "string", "minLength": 1},
        "language": {"type": "string", "minLength": 1},
        "part_of_speech_id": {"type": "integer"},
        "category_ids": {
            "type": "array",
            "items": {"type": "string", "minLength": 1},
        },
    },
    "additionalProperties": False,
}

TRANSLATION_CREATE_SCHEMA = {
    "type": "object",
    "required": ["text", "language"],
    "properties": {
        "text": {"type": "string", "minLength": 1},
        "language": {"type": "string", "minLength": 1},
        "note": {"type": ["string", "null"]},
    },
    "additionalProperties": False,
}

TRANSLATION_UPDATE_SCHEMA = {
    "type": "object",
    "required": ["word_id", "text", "language", "note"],
    "properties": {
        "word_id": {"type": "string", "minLength": 1},
        "text": {"type": "string", "minLength": 1},
        "language": {"type": "string", "minLength": 1},
        "note": {"type": ["string", "null"]},
    },
    "additionalProperties": False,
}

CATEGORY_CREATE_SCHEMA = {
    "type": "object",
    "required": ["name", "user_id"],
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "user_id": {"type": "string", "minLength": 1},
    },
    "additionalProperties": False,
}

CATEGORY_UPDATE_SCHEMA = {
    "type": "object",
    "required": ["user_id", "name"],
    "properties": {
        "user_id": {"type": "string", "minLength": 1},
        "name": {"type": "string", "minLength": 1},
    },
    "additionalProperties": False,
}

PART_OF_SPEECH_CREATE_SCHEMA = {
    "type": "object",
    "required": ["code", "name"],
    "properties": {
        "code": {"type": "string", "minLength": 1},
        "name": {"type": "string", "minLength": 1},
    },
    "additionalProperties": False,
}

PART_OF_SPEECH_UPDATE_SCHEMA = {
    "type": "object",
    "required": ["code", "name"],
    "properties": {
        "code": {"type": "string", "minLength": 1},
        "name": {"type": "string", "minLength": 1},
    },
    "additionalProperties": False,
}


def _format_error(error):
    """Convert a jsonschema error into a compact human-readable message."""
    location = ".".join(str(part) for part in error.path)
    if location:
        return f"{location}: {error.message}"
    return error.message


def validate_request_json(request, schema):
    """Return validated JSON or a 400-compatible error response tuple."""
    data = request.get_json(silent=True)
    if data is None:
        return None, ({"error": "invalid JSON body"}, 400)

    validator = Draft7Validator(schema, format_checker=FORMAT_CHECKER)
    errors = sorted(validator.iter_errors(data), key=lambda item: list(item.path))
    if errors:
        return None, (
            {
                "error": "invalid request body",
                "details": [_format_error(error) for error in errors],
            },
            400,
        )

    return data, None
