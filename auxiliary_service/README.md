# Study Pack Service

This folder contains the Deadline 5 auxiliary service.

## Purpose

The service consumes the main Personal Word Repository API and produces
study-oriented derived responses such as:

- random study packs
- words missing translations
- words grouped by category

This keeps derived learning logic outside the main CRUD API.

## Endpoints

- `GET /healthz`
- `GET /study-pack/random`
- `GET /study-pack/missing-translations`
- `GET /study-pack/by-category`

All study-pack endpoints validate their query parameters and derive their
responses from the live main API.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Quality checks

Install the shared development dependencies from the project root if needed:

```bash
pip install -r requirements-dev.txt
```

Then run:

```bash
python -m pylint client auxiliary_service wordrepo --disable=missing-module-docstring,missing-function-docstring,missing-class-docstring,import-outside-toplevel,redefined-outer-name,too-many-public-methods,too-many-arguments,too-many-positional-arguments,too-many-locals,too-few-public-methods,trailing-whitespace,trailing-newlines,duplicate-code,cyclic-import
python -m pytest -q tests/test_auxiliary_service.py
```

## Configuration

Environment variables:

- `MAIN_API_BASE_URL`
  - default: `http://127.0.0.1:5000`
- `PORT`
  - default: `5050`

## Deploying in Rahti

The repository includes a dedicated Dockerfile for the auxiliary service:

```text
auxiliary_service/Dockerfile
```

When importing the same repository into Rahti for this service, use:

- Dockerfile path: `auxiliary_service/Dockerfile`
- environment variable `MAIN_API_BASE_URL` pointing to the online main API route

The service listens on the platform-provided `PORT` value and can be exposed
through its own route.

## Current state

The service fetches words, categories, and translations from the main API and
returns derived study-oriented responses for the client.

## Limitations

- The service computes results on demand and does not maintain its own cached
  storage yet.
- If the main API is unavailable, study-pack endpoints return a readable `502`
  response.
