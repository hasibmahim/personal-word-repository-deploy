"""Resource module for managing words."""

import uuid

from flask import request
from flask_restful import Resource

from wordrepo.models import Category, PartOfSpeech, User, Word, db
from wordrepo.validation import (
    WORD_CREATE_SCHEMA,
    WORD_UPDATE_SCHEMA,
    validate_request_json,
)


def word_to_dict(word):
    """Serialize a word for API responses."""
    return {
        "id": word.id,
        "user_id": word.user_id,
        "text": word.text,
        "language": word.language,
        "part_of_speech_id": word.part_of_speech_id,
        "categories": [category.id for category in word.categories],
    }


class WordListResource(Resource):
    """Handles collection operations for words."""

    def get(self):
        """List words, optionally filtered by user or category."""
        user_id = request.args.get("user_id")
        category_id = request.args.get("category_id")

        query = Word.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        if category_id:
            query = query.join(Word.categories).filter(Category.id == category_id)

        words = query.order_by(Word.created_at.asc(), Word.text.asc()).all()
        return [word_to_dict(word) for word in words], 200

    def post(self):
        """Create a new word."""
        data, error = validate_request_json(request, WORD_CREATE_SCHEMA)
        if error:
            return error

        if not db.session.get(User, data["user_id"]):
            return {"error": "user not found"}, 404

        if not db.session.get(PartOfSpeech, data["part_of_speech_id"]):
            return {"error": "part_of_speech not found"}, 404

        new_word = Word(
            id=str(uuid.uuid4()),
            user_id=data["user_id"],
            text=data["text"],
            language=data["language"],
            part_of_speech_id=data["part_of_speech_id"],
        )

        if "category_ids" in data:
            for cid in data["category_ids"]:
                category = db.session.get(Category, cid)
                if not category:
                    return {"error": f"category not found: {cid}"}, 404
                new_word.categories.append(category)

        db.session.add(new_word)
        db.session.commit()
        return word_to_dict(new_word), 201


class WordResource(Resource):
    """Handles GET, PUT, DELETE for words."""

    def get(self, word_id):
        """Retrieve a single word."""
        word = db.session.get(Word, word_id)
        if not word:
            return {"error": "word not found"}, 404
        return word_to_dict(word), 200

    def put(self, word_id):
        """Replace a word's mutable fields with a full representation."""
        word = db.session.get(Word, word_id)
        if not word:
            return {"error": "word not found"}, 404

        data, error = validate_request_json(request, WORD_UPDATE_SCHEMA)
        if error:
            return error

        if data["user_id"] != word.user_id:
            return {"error": "user_id does not match the existing word owner"}, 400

        if not db.session.get(PartOfSpeech, data["part_of_speech_id"]):
            return {"error": "part_of_speech not found"}, 404

        categories = []
        for cid in data["category_ids"]:
            category = db.session.get(Category, cid)
            if not category:
                return {"error": f"category not found: {cid}"}, 404
            categories.append(category)

        word.text = data["text"]
        word.language = data["language"]
        word.part_of_speech_id = data["part_of_speech_id"]
        word.categories = categories

        db.session.commit()
        return word_to_dict(word), 200

    def delete(self, word_id):
        """Delete a word."""
        word = db.session.get(Word, word_id)
        if not word:
            return {"error": "word not found"}, 404

        db.session.delete(word)
        db.session.commit()
        return "", 204
