"""Resource module for managing users."""

import uuid

from flask import request
from flask_restful import Resource
from werkzeug.security import generate_password_hash

from wordrepo.models import User, db
from wordrepo.validation import (
    USER_CREATE_SCHEMA,
    USER_UPDATE_SCHEMA,
    validate_request_json,
)

API_KEY = "API_KEY_12345"

def user_to_dict(user):
    """Serialize a user for API responses."""
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at.isoformat(),
    }


class UserListResource(Resource):
    """Handles GET and POST for users."""

    def get(self):
        """Return all users when the static bearer token is present."""
        key = request.headers.get("Authorization")
        if key != f"Bearer {API_KEY}":
            return {"error": "unauthorized"}, 401

        users = User.query.all()
        return [user_to_dict(u) for u in users], 200

    def post(self):
        """Create a new user."""
        data, error = validate_request_json(request, USER_CREATE_SCHEMA)
        if error:
            return error

        if User.query.filter_by(email=data["email"]).first():
            return {"error": "email already in use"}, 409

        new_user = User(
            id=str(uuid.uuid4()),
            email=data["email"],
            password_hash=generate_password_hash(data["password"]),
        )
        db.session.add(new_user)
        db.session.commit()
        return user_to_dict(new_user), 201


class UserResource(Resource):
    """Handles GET, PUT, DELETE for users."""

    def get(self, user_id):
        """Retrieve a single user by ID."""
        user = db.session.get(User, user_id)
        if not user:
            return {"error": "user not found"}, 404
        return user_to_dict(user), 200

    def put(self, user_id):
        """Replace a user's mutable fields with a full representation."""
        user = db.session.get(User, user_id)
        if not user:
            return {"error": "user not found"}, 404

        data, error = validate_request_json(request, USER_UPDATE_SCHEMA)
        if error:
            return error

        existing_user = User.query.filter_by(email=data["email"]).first()
        if existing_user and existing_user.id != user.id:
            return {"error": "email already in use"}, 409

        user.email = data["email"]
        user.password_hash = generate_password_hash(data["password"])

        db.session.commit()
        return user_to_dict(user), 200

    def delete(self, user_id):
        """Delete a user."""
        user = db.session.get(User, user_id)
        if not user:
            return {"error": "user not found"}, 404

        db.session.delete(user)
        db.session.commit()
        return "", 204
