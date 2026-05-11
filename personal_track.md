# Personal Track

This file tracks work done after Deadline 4 so the project history stays easy to explain during the final meeting.

## Current strategy

1. Keep the Deadline 4 API stable and demonstrably working first.
2. Build Deadline 5 features locally in small verified steps.
3. Deploy Deadline 5 updates to Rahti only after the local version is working and documented.

## Deadline 4 baseline status

- Main API implemented and documented
- Automated tests expanded and passing
- Coverage raised to 100%
- Wiki report saved in `WIKI_REPORT.md`
- API deployed to Rahti
- Public route verified after route recreation

## Post-Deadline-4 work log

### 2026-04-07

- Reviewed Deadline 5 rubric and chose a web client plus auxiliary service approach.
- Defined the client screens, use cases, and workflow.
- Defined the auxiliary `Study Pack Service` idea and its planned endpoints.
- Added starter folders:
  - `client/`
  - `auxiliary_service/`
- Added a static client scaffold with starter README, HTML, CSS, and JavaScript.
- Added a Flask scaffold for the auxiliary service with starter endpoints.
- Cleaned the API resource modules for readability.
- Replaced legacy SQLAlchemy `Query.get()` calls with `db.session.get(...)`.
- Added comments to explain essential logic where it helps future readers.
- Temporarily explored a browser client prototype, then pivoted away from it to stay closer to the course tool guidance.
- Replaced the browser client direction with a Python terminal client using `requests`.
- Implemented the first real terminal client behavior:
  - create and load users
  - fetch parts of speech
  - create/edit/delete tracked words
  - create/edit/delete tracked categories
  - create/edit/delete translations for a selected word
  - dashboard summary
- Re-ran tests successfully after the API and client-serving changes.

### 2026-05-11

- Added collection reads to the main API:
  - `GET /words`
  - `GET /categories`
- Updated the OpenAPI specification and API tests for the new list endpoints.
- Replaced the auxiliary service placeholder responses with live fetches from the main API.
- Added auxiliary service tests for both derived study-pack behavior and route validation.
- Upgraded the terminal client to:
  - browse live words and categories
  - connect to the auxiliary study-pack service
  - show random, missing-translation, and category-based study packs
- Added client helper tests.
- Refreshed the Deadline 5 planning and evidence documents so they match the implemented state.

## Next recommended steps

1. Re-verify Deadline 4 deliverables locally and on Rahti.
2. Push only stable changes.
3. Continue Deadline 5 implementation locally with the Python terminal client and auxiliary service.
4. Deploy the updated auxiliary service later after local verification.
