"""Resource module for managing translations."""

import uuid

from flask import request
from flask_restful import Resource

from wordrepo.models import Translation, Word, db
from wordrepo.validation import (
    TRANSLATION_CREATE_SCHEMA,
    TRANSLATION_UPDATE_SCHEMA,
    validate_request_json,
)


def translation_to_dict(translation):
    """Serialize a translation for API responses."""
    return {
        "id": translation.id,
        "word_id": translation.word_id,
        "text": translation.text,
        "language": translation.language,
        "note": translation.note,
    }


class TranslationListResource(Resource):
    """Handles GET, POST for translations."""

    def get(self, word_id):
        """Return all translations for a given word."""
        word = db.session.get(Word, word_id)
        if not word:
            return {"error": "word not found"}, 404

        translations = Translation.query.filter_by(word_id=word_id).all()
        return [translation_to_dict(translation) for translation in translations], 200

    def post(self, word_id):
        """Create a new translation for a given word."""
        word = db.session.get(Word, word_id)
        if not word:
            return {"error": "word not found"}, 404

        data, error = validate_request_json(request, TRANSLATION_CREATE_SCHEMA)
        if error:
            return error

        new_translation = Translation(
            id=str(uuid.uuid4()),
            word_id=word_id,
            text=data["text"],
            language=data["language"],
            note=data.get("note"),
        )
        db.session.add(new_translation)
        db.session.commit()
        return translation_to_dict(new_translation), 201


class TranslationResource(Resource):
    """Handles GET, PUT, DELETE for translations."""

    def get(self, translation_id):
        """Retrieve a single translation."""
        translation = db.session.get(Translation, translation_id)
        if not translation:
            return {"error": "translation not found"}, 404
        return translation_to_dict(translation), 200

    def put(self, translation_id):
        """Replace a translation's mutable fields with a full representation."""
        translation = db.session.get(Translation, translation_id)
        if not translation:
            return {"error": "translation not found"}, 404

        data, error = validate_request_json(request, TRANSLATION_UPDATE_SCHEMA)
        if error:
            return error

        if data["word_id"] != translation.word_id:
            return {"error": "word_id does not match the existing translation owner"}, 400

        translation.text = data["text"]
        translation.language = data["language"]
        translation.note = data["note"]

        db.session.commit()
        return translation_to_dict(translation), 200

    def delete(self, translation_id):
        """Delete a translation."""
        translation = db.session.get(Translation, translation_id)
        if not translation:
            return {"error": "translation not found"}, 404

        db.session.delete(translation)
        db.session.commit()
        return "", 204
