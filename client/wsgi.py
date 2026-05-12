"""WSGI entrypoint for the browser-based GUI client."""

from client.web import create_web_app

app = create_web_app()
