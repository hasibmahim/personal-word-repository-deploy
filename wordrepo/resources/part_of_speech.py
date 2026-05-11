"""Resource module for managing parts of speech."""

import hashlib
import json

from flask import make_response, request
from flask_restful import Resource

from wordrepo.models import PartOfSpeech, db
from wordrepo.validation import (
    PART_OF_SPEECH_CREATE_SCHEMA,
    PART_OF_SPEECH_UPDATE_SCHEMA,
    validate_request_json,
)


def pos_to_dict(pos):
    """Serialize a part of speech for API responses."""
    return {
        "id": pos.id,
        "code": pos.code,
        "name": pos.name,
        "words": [word.id for word in pos.words],
    }


class PartOfSpeechListResource(Resource):
    """Handles GET and POST for parts of speech."""

    def get(self):
        """Return all parts of speech."""
        parts = PartOfSpeech.query.all()
        payload = [pos_to_dict(p) for p in parts]

        # The ETag is derived from the serialized response so caches are
        # invalidated automatically whenever the list contents change.
        etag = hashlib.sha256(
            json.dumps(payload, sort_keys=True).encode("utf-8")
        ).hexdigest()

        if request.if_none_match.contains(etag):
            response = make_response("", 304)
        else:
            response = make_response(payload, 200)

        response.set_etag(etag)
        response.headers["Cache-Control"] = "public, max-age=300"
        return response

    def post(self):
        """Create a part of speech."""
        data, error = validate_request_json(request, PART_OF_SPEECH_CREATE_SCHEMA)
        if error:
            return error

        if PartOfSpeech.query.filter_by(code=data["code"]).first():
            return {"error": "part of speech already exists"}, 409

        new_pos = PartOfSpeech(code=data["code"], name=data["name"])

        db.session.add(new_pos)
        db.session.commit()

        return pos_to_dict(new_pos), 201


class PartOfSpeechResource(Resource):
    """Handles PUT and DELETE for parts of speech."""

    def put(self, pos_id):
        """Update a part of speech."""
        pos = db.session.get(PartOfSpeech, pos_id)
        if not pos:
            return {"error": "part of speech not found"}, 404

        data, error = validate_request_json(request, PART_OF_SPEECH_UPDATE_SCHEMA)
        if error:
            return error

        if "name" in data:
            pos.name = data["name"]

        db.session.commit()
        return pos_to_dict(pos), 200

    def delete(self, pos_id):
        """Delete a part of speech."""
        pos = db.session.get(PartOfSpeech, pos_id)
        if not pos:
            return {"error": "part of speech not found"}, 404

        db.session.delete(pos)
        db.session.commit()
        return {"message": "part of speech deleted"}, 200
