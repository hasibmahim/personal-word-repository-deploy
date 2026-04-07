"""Category resource module for the Personal Word Repository."""
import uuid
from flask import request
from flask_restful import Resource
from wordrepo.models import db, Category, User
from wordrepo.validation import (
    CATEGORY_CREATE_SCHEMA,
    CATEGORY_UPDATE_SCHEMA,
    validate_request_json,
)

def category_to_dict(category):
    """Creates a dictionary for category."""
    return {
        "id": category.id,
        "user_id": category.user_id,
        "name": category.name,
        "words": [w.id for w in category.words]
    }

class CategoryListResource(Resource):
    """Handles POST for categories."""
    def post(self):
        """Create a new category."""
        data, error = validate_request_json(request, CATEGORY_CREATE_SCHEMA)
        if error:
            return error
        #validate the user
        user = User.query.get(data["user_id"])
        if not user:
            return {"error": "user not found"}, 404
        existing_category = Category.query.filter_by(
            user_id=data["user_id"],
            name=data["name"]
        ).first()
        if existing_category:
            return {"error": "category already exists for user"}, 409
        new_category = Category(
            id=str(uuid.uuid4()),
            user_id=data["user_id"],
            name=data["name"]
            )
        db.session.add(new_category)
        db.session.commit()
        return category_to_dict(new_category), 201

class CategoryResource(Resource):
    """Handles GET, PUT, DELETE for categories."""
    def get(self, category_id):
        """Retrieve a single category"""
        category = Category.query.get(category_id)
        if not category:
            return {"error": "category not found"}, 404
        return category_to_dict(category), 200
    def put(self, category_id):
        """Update a category"""
        category = Category.query.get(category_id)
        if not category:
            return {"error": "category not found"}, 404
        data, error = validate_request_json(request, CATEGORY_UPDATE_SCHEMA)
        if error:
            return error
        if "name" in data:
            existing_category = Category.query.filter_by(
                user_id=category.user_id,
                name=data["name"]
            ).first()
            if existing_category and existing_category.id != category.id:
                return {"error": "category already exists for user"}, 409
            category.name = data["name"]
        db.session.commit()
        return category_to_dict(category), 200
    def delete(self, category_id):
        """Delete a category."""
        category = Category.query.get(category_id)
        if not category:
            return {"error": "category not found"}, 404
        db.session.delete(category)
        db.session.commit()
        return {"message": "category deleted"}, 200
