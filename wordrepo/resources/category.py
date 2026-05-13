"""Category resource module for the Personal Word Repository."""

import uuid

from flask import request
from flask_restful import Resource

from wordrepo.models import Category, User, db
from wordrepo.validation import (
    CATEGORY_CREATE_SCHEMA,
    CATEGORY_UPDATE_SCHEMA,
    validate_request_json,
)


def category_to_dict(category):
    """Serialize a category for API responses."""
    return {
        "id": category.id,
        "user_id": category.user_id,
        "name": category.name,
        "words": [word.id for word in category.words],
    }


class CategoryListResource(Resource):
    """Handles collection operations for categories."""

    def get(self):
        """List categories, optionally filtered by user."""
        user_id = request.args.get("user_id")

        query = Category.query
        if user_id:
            query = query.filter_by(user_id=user_id)

        categories = query.order_by(Category.name.asc()).all()
        return [category_to_dict(category) for category in categories], 200

    def post(self):
        """Create a new category."""
        data, error = validate_request_json(request, CATEGORY_CREATE_SCHEMA)
        if error:
            return error

        user = db.session.get(User, data["user_id"])
        if not user:
            return {"error": "user not found"}, 404

        existing_category = Category.query.filter_by(
            user_id=data["user_id"],
            name=data["name"],
        ).first()
        if existing_category:
            return {"error": "category already exists for user"}, 409

        new_category = Category(
            id=str(uuid.uuid4()),
            user_id=data["user_id"],
            name=data["name"],
        )
        db.session.add(new_category)
        db.session.commit()
        return category_to_dict(new_category), 201


class CategoryResource(Resource):
    """Handles GET, PUT, DELETE for categories."""

    def get(self, category_id):
        """Retrieve a single category."""
        category = db.session.get(Category, category_id)
        if not category:
            return {"error": "category not found"}, 404
        return category_to_dict(category), 200

    def put(self, category_id):
        """Replace a category's mutable fields with a full representation."""
        category = db.session.get(Category, category_id)
        if not category:
            return {"error": "category not found"}, 404

        data, error = validate_request_json(request, CATEGORY_UPDATE_SCHEMA)
        if error:
            return error

        if data["user_id"] != category.user_id:
            return {"error": "user_id does not match the existing category owner"}, 400

        existing_category = Category.query.filter_by(
            user_id=category.user_id,
            name=data["name"],
        ).first()
        if existing_category and existing_category.id != category.id:
            return {"error": "category already exists for user"}, 409

        category.name = data["name"]

        db.session.commit()
        return category_to_dict(category), 200

    def delete(self, category_id):
        """Delete a category."""
        category = db.session.get(Category, category_id)
        if not category:
            return {"error": "category not found"}, 404

        db.session.delete(category)
        db.session.commit()
        return "", 204
