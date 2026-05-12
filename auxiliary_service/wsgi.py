"""WSGI entrypoint for the auxiliary study-pack service."""

from auxiliary_service.app import create_app

app = create_app()
