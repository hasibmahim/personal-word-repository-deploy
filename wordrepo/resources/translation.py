"""Resource module for managing translation."""
import uuid
from flask import request
from flask_restful import Resource
from wordrepo.models import db, Translation, Word
from wordrepo.validation import (
    TRANSLATION_CREATE_SCHEMA,
    TRANSLATION_UPDATE_SCHEMA,
    validate_request_json,
)

def translation_to_dict(t):
    """Creates a dictionary for translation."""
    return {
        "id": t.id,
        "word_id": t.word_id,
        "text": t.text,
        "language": t.language,
        "note": t.note
    }

class TranslationListResource(Resource):
    """Handles GET, POST for translations."""
    def get(self, word_id):
        """Return all translations for a given word."""
        word = Word.query.get(word_id)
        if not word:
            return {"error": "word not found"}, 404
        translation = Translation.query.filter_by(word_id=word_id).all()
        return [translation_to_dict(t) for t in translation], 200
    def post(self, word_id):
        """Create a new translation for a given word."""
        word = Word.query.get(word_id)
        if not word:
            return {"error": "word not found"}, 404
        data, error = validate_request_json(request, TRANSLATION_CREATE_SCHEMA)
        if error:
            return error
        new_translation = Translation(
           id = str(uuid.uuid4()),
           word_id = word_id,
           text = data["text"],
           language = data["language"],
           note = data.get("note")
           )
        db.session.add(new_translation)
        db.session.commit()
        return translation_to_dict(new_translation), 201

class TranslationResource(Resource):
    """Handles GET, PUT, DELETE for translations."""
    def get(self, translation_id):
        """Retrieve a single translation"""
        t = Translation.query.get(translation_id)
        if not t:
            return {"error": "translation not found"}, 404
        return translation_to_dict(t), 200
    def put(self, translation_id):
        """Update a translation"""
        t = Translation.query.get(translation_id)
        if not t:
            return {"error": "translation not found"}, 404
        data, error = validate_request_json(request, TRANSLATION_UPDATE_SCHEMA)
        if error:
            return error
        if "text" in data:
            t.text = data["text"]
        if "language" in data:
            t.language = data["language"]
        if "note" in data:
            t.note = data["note"]
        db.session.commit()
        return translation_to_dict(t), 200
    def delete(self, translation_id):
        """Delete a translation"""
        t = Translation.query.get(translation_id)
        if not t:
            return {"error": "translation not found"}, 404
        db.session.delete(t)
        db.session.commit()
        return {"message": "translation deleted"}, 200
