"""API initialization module for the Personal Word Repository."""
import os
from pathlib import Path

from flask import Flask, Response, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api

db = SQLAlchemy()
OPENAPI_PATH = Path(__file__).resolve().parent.parent / "docs" / "openapi.yaml"
SWAGGER_UI_HTML = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Personal Word Repository API Docs</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
      window.ui = SwaggerUIBundle({
        url: "/openapi.yaml",
        dom_id: "#swagger-ui"
      });
    </script>
  </body>
</html>
"""

def create_app(config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        "sqlite:///words.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if config:
        app.config.update(config)

    db.init_app(app)
    api = Api(app)

    #import resources
    from wordrepo.resources.user import UserListResource, UserResource
    from wordrepo.resources.word import WordListResource, WordResource
    from wordrepo.resources.translation import TranslationListResource, TranslationResource
    from wordrepo.resources.category import CategoryListResource, CategoryResource
    from wordrepo.resources.part_of_speech import PartOfSpeechListResource, PartOfSpeechResource

    #User endpoints
    api.add_resource(UserListResource, "/users")
    api.add_resource(UserResource, "/users/<string:user_id>")
    #Word endpoints
    api.add_resource(WordListResource, "/words")
    api.add_resource(WordResource, "/words/<string:word_id>")
    #Translation endpoints
    api.add_resource(TranslationListResource, "/words/<string:word_id>/translations")
    api.add_resource(TranslationResource, "/translations/<string:translation_id>")
    # Category endpoints
    api.add_resource(CategoryListResource, "/categories")
    api.add_resource(CategoryResource, "/categories/<string:category_id>")
    # Part of Speech endpoints
    api.add_resource(PartOfSpeechListResource, "/parts-of-speech")
    api.add_resource(PartOfSpeechResource, "/parts-of-speech/<string:pos_id>")

    @app.get("/openapi.yaml")
    def openapi_spec():
        """Serve the OpenAPI specification file."""
        return send_file(OPENAPI_PATH, mimetype="application/yaml")

    @app.get("/docs")
    @app.get("/docs/")
    def swagger_ui():
        """Serve Swagger UI for the OpenAPI specification."""
        return Response(SWAGGER_UI_HTML, mimetype="text/html")

    @app.get("/healthz")
    def healthz():
        """Health endpoint for platform probes."""
        return {"status": "ok"}, 200

    return app
