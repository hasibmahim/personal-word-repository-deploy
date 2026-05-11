# Client Overview

## What the client does

The Deadline 5 client is a Python terminal application that helps a learner manage personal vocabulary through the Personal Word Repository API. It supports the common workflow of creating a user, adding categories, creating words with parts of speech, and attaching translations to those words.

## Why this client was chosen

The terminal client stays close to the tools already used in the course stack: Python and HTTP-based API work. It also demonstrates more than simple endpoint calls by maintaining local session state, guiding the user through multi-step flows, and presenting a consistent interactive interface.

## Feature-to-endpoint mapping

| Client feature | Endpoint | Method | Purpose | Success and handled error cases |
| --- | --- | --- | --- | --- |
| API health check on startup | `/healthz` | `GET` | Confirm the API is reachable before interaction begins | Success `200`; network failures become readable `ApiError` messages |
| Create user | `/users` | `POST` | Register a user for storing words | Success `201`; validation `400`; duplicate email `409` |
| Load saved user | Local state only | N/A | Switch active user in the terminal client | Local input validation only |
| List words for active user | `/words?user_id=...` | `GET` | Show all live words for the current user | Success `200`; request failures shown to the user |
| List parts of speech | `/parts-of-speech` | `GET` | Show valid part-of-speech IDs before word creation | Success `200`; request failures shown to the user |
| Create word | `/words` | `POST` | Add vocabulary for the active user | Success `201`; validation `400`; reference or duplicate errors surfaced through `ApiError` |
| Inspect selected word | `/words/{word_id}` | `GET` | Load the currently selected word when entering translations | Success `200`; missing-resource errors shown |
| Update word | `/words/{word_id}` | `PUT` | Edit text, language, part of speech, or categories | Success `200`; validation or missing-resource errors shown |
| Delete word | `/words/{word_id}` | `DELETE` | Remove a tracked word | Success `200`; missing-resource errors shown |
| Create category | `/categories` | `POST` | Add a reusable grouping for words | Success `201`; validation and API errors shown |
| List categories for active user | `/categories?user_id=...` | `GET` | Show all live categories for the current user | Success `200`; request failures shown to the user |
| Update category | `/categories/{category_id}` | `PUT` | Rename a category | Success `200`; validation or missing-resource errors shown |
| Delete category | `/categories/{category_id}` | `DELETE` | Remove a category | Success `200`; API errors shown |
| List translations | `/words/{word_id}/translations` | `GET` | Show translations for the selected word | Success `200`; failures shown without crashing |
| Create translation | `/words/{word_id}/translations` | `POST` | Add a translation to a word | Success `201`; validation errors shown |
| Update translation | `/translations/{translation_id}` | `PUT` | Edit a translation | Success `200`; validation or missing-resource errors shown |
| Delete translation | `/translations/{translation_id}` | `DELETE` | Remove a translation | Success `200`; API errors shown |
| Random study pack | `/study-pack/random` | `GET` | Show a derived random study set from the auxiliary service | Success `200`; validation `400`; upstream failures `502` |
| Missing-translations study pack | `/study-pack/missing-translations` | `GET` | Show words that still need translations | Success `200`; validation `400`; upstream failures `502` |
| Category study pack | `/study-pack/by-category` | `GET` | Show study items from one category | Success `200`; validation `400`; upstream failures `502` |

## Error-handling strategy

- The HTTP wrapper in `client/api_client.py` converts network and HTTP failures into `ApiError`.
- The auxiliary-service wrapper in `client/study_pack_client.py` converts failures into `StudyPackError`.
- The terminal UI catches `ApiError` close to each workflow and prints a contextual message instead of a stack trace.
- The terminal UI also catches `StudyPackError` when the study-pack service is unavailable or returns an upstream error.

## Limitations

- The client is menu-driven and text-based, not graphical.
- The client still relies on a small local state file for saved users and the active selected word.
