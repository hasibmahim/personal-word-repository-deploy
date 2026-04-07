# Deadline 3 Wiki Report

## Overview

The Personal Word Repository API is a RESTful service for storing, categorizing, and translating personal vocabulary. The API supports users, words, translations, categories, and parts of speech. The implementation follows a resource-oriented design, uses standard HTTP methods consistently, validates incoming JSON request bodies, and stores persistent data in a relational database through SQLAlchemy.

## Resource Table

| Resource | URI | Methods | Description |
|---|---|---|---|
| Users collection | `/users` | `GET`, `POST` | List users and create a new user |
| Single user | `/users/{user_id}` | `GET`, `PUT`, `DELETE` | Retrieve, update, or delete one user |
| Words collection | `/words` | `POST` | Create a new word |
| Single word | `/words/{word_id}` | `GET`, `PUT`, `DELETE` | Retrieve, update, or delete one word |
| Word translations collection | `/words/{word_id}/translations` | `GET`, `POST` | List translations for one word and create a translation |
| Single translation | `/translations/{translation_id}` | `GET`, `PUT`, `DELETE` | Retrieve, update, or delete one translation |
| Categories collection | `/categories` | `POST` | Create a new category |
| Single category | `/categories/{category_id}` | `GET`, `PUT`, `DELETE` | Retrieve, update, or delete one category |
| Parts of speech collection | `/parts-of-speech` | `GET`, `POST` | List all parts of speech and create a new one |
| Single part of speech | `/parts-of-speech/{pos_id}` | `PUT`, `DELETE` | Update or delete one part of speech |
| Health endpoint | `/healthz` | `GET` | Simple deployment health check |
| OpenAPI spec | `/openapi.yaml` | `GET` | Raw OpenAPI documentation |
| Swagger UI | `/docs` | `GET` | Interactive API documentation |

## Addressability

The API is fully addressable because each resource has its own stable URI. Collections and individual resources are separated clearly. For example, `/users` refers to the user collection, while `/users/{user_id}` refers to one specific user. The same pattern is used for words, categories, translations, and parts of speech.

The hierarchy is also consistent. Translations belong to words, so listing or creating translations uses `/words/{word_id}/translations`. This expresses the relationship directly in the URI and makes the API easier to understand. A client can create a word first, then use that word identifier to create or fetch related translations.

## Uniform Interface

The API uses HTTP methods according to their intended meaning:

- `GET` retrieves resource representations, for example `/users/{user_id}` and `/parts-of-speech`.
- `POST` creates new resources, for example `/users`, `/words`, `/categories`, and `/words/{word_id}/translations`.
- `PUT` updates an existing resource, for example `/users/{user_id}` and `/translations/{translation_id}`.
- `DELETE` removes a resource, for example `/words/{word_id}` and `/categories/{category_id}`.

This method usage is consistent across the API, which supports the REST uniform interface principle. Response codes also follow the same idea: `200` for success, `201` for resource creation, `400` for invalid requests, `401` for unauthorized access, `404` for missing resources, and `409` for conflicts such as duplicate values.

## Statelessness

The API is stateless because each request contains all information needed to process it. The server does not keep per-client session state between requests. If the client wants protected access to `GET /users`, it must send the bearer token in the `Authorization` header every time. The server checks the header on that request only and does not rely on a stored login session.

The database stores application data such as users, words, categories, and translations, but this is resource state, not client session state. Because requests are independent, the API remains stateless.

## Connectedness

Connectedness is achieved through relationships between resources and identifiers returned in representations. For example:

- a word contains `user_id`, so the client can connect the word to its owner
- a word contains `part_of_speech_id`, linking it to one part of speech
- a category representation contains a list of related word identifiers
- translations are connected to a word through `/words/{word_id}/translations`

This means a client can navigate the application domain through the data returned by the API. After retrieving a word, the client knows its part of speech and can also request its translations. This creates a connected resource structure rather than isolated endpoints.

## Project Structure

The project follows a modular structure instead of a single-file application. The main application factory is in `wordrepo/api.py`, the database models are in `wordrepo/models.py`, and each main resource type is implemented in its own file under `wordrepo/resources`. This keeps the implementation easier to maintain and closer to good Flask project structure.

The project also separates:

- runtime dependencies in `requirements.txt`
- developer and testing dependencies in `requirements-dev.txt`
- tests in `tests/test_api.py`
- OpenAPI documentation in `docs/openapi.yaml`

## Code Quality

The implementation follows idiomatic Python structure and was checked with PyLint. The required disabled warnings were the ones allowed by the assignment instructions. In addition, the application code was verified by automated tests and coverage measurement. The resource handlers are short and focused, and repeated validation logic was centralized instead of being duplicated in every endpoint.

## Documentation

The code is documented where needed through concise docstrings in the resource modules and helper functions. The repository also contains:

- installation and deployment instructions in `README.md`
- an OpenAPI 3.0 specification in `docs/openapi.yaml`
- live Swagger UI at `/docs`

If AI-assisted development must be disclosed, this project can state that AI assistance was used for implementation support, testing support, and wording refinement, together with the tool name and the kinds of prompts that were used.

## Instructions

The project root README explains how to:

- create and activate a virtual environment
- install runtime and development dependencies
- initialize the database
- run the API locally
- run the API with Docker
- run the automated tests
- generate the coverage report
- deploy the API using CSC services

## Test Coverage

Automated tests were implemented for all main resource types and important success and error paths. The test suite covers:

- user creation, retrieval, updating, deletion, duplicate email handling, and authorization
- word creation, retrieval, updating, deletion, category assignment, and missing dependency cases
- category creation, retrieval, updating, deletion, duplicate handling, and missing user cases
- translation creation, retrieval, updating, deletion, and missing word or translation cases
- parts of speech creation, updating, deletion, duplicate handling, and caching behavior
- documentation and health endpoints
- invalid JSON and invalid request body handling

Coverage was measured with:

```bash
python -m pytest --cov=wordrepo --cov-report=term-missing
```

The verified result was `100%` total coverage for the `wordrepo` package.

## Implementation Works

The implementation was verified in two ways:

- automated tests passed successfully
- the API was deployed and demonstrated through the live Rahti route

The live deployment exposes:

- `/healthz`
- `/docs`
- `/openapi.yaml`

This means both the local implementation and the deployed version were demonstrated to work.

## URL Converters

The API currently uses plain path parameters such as `{user_id}`, `{word_id}`, `{category_id}`, `{translation_id}`, and `{pos_id}` rather than custom Flask URL converters. This choice is justified because the project already validates resource existence and request correctness inside the handlers, and most identifiers are UUID-like strings that are passed through consistently. For `pos_id`, an integer-like identifier is used in the API design and documented accordingly in OpenAPI. A custom converter could be added later, but it was not strictly necessary for correctness in this project.

## Schema Validation

Incoming JSON request bodies are validated using JSON Schema in `wordrepo/validation.py`. Each write operation uses a dedicated schema, for example:

- user create and update
- word create and update
- translation create and update
- category create and update
- part-of-speech create and update

This validation checks required fields, types, selected formats such as email, and disallows unexpected extra fields with `additionalProperties: false`. This makes request handling safer and more predictable and reduces duplicated manual validation logic in the resource handlers.

## Caching

Caching is implemented for `GET /parts-of-speech`. This endpoint is a good candidate because parts of speech are relatively stable compared with user-created words and translations. The API returns:

- an `ETag` header based on the serialized response
- `Cache-Control: public, max-age=300`

If the client later sends the same ETag in `If-None-Match`, the endpoint returns `304 Not Modified`. Cache invalidation is handled naturally because when the underlying parts-of-speech data changes, the serialized response changes, which changes the computed ETag value.

## Authentication

Authentication is used for `GET /users`. The endpoint requires a bearer token in the `Authorization` header and returns `401 Unauthorized` if the token is missing or invalid. This demonstrates authenticated access in the API.

Other endpoints were intentionally left unauthenticated in this project to keep the implementation smaller and easier to demonstrate while still showing at least one protected resource. This should be explained as a scope decision rather than a claim that unrestricted access would be appropriate in a production system.

## Deployment Summary

The API was deployed on CSC infrastructure using:

- `Rahti` for the running container
- `Pukki` for persistent PostgreSQL storage
- `Gunicorn` as the WSGI application server
- `NGINX` as the web server and reverse proxy
- `Supervisor` to manage the processes inside the container

This deployment makes the API publicly accessible while keeping data persistent outside the application container.
