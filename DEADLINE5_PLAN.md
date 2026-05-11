# Deadline 5 Summary

This file collects the main points to show during review and the checks that were completed locally.

## 1) Delivered scope

### Main API additions completed for Deadline 5

- `GET /words`
  Optional filters: `user_id`, `category_id`
- `GET /categories`
  Optional filter: `user_id`

These collection reads were added so the terminal client and auxiliary service can work from live API data instead of locally tracked IDs.

### Client delivered

- Python terminal client in `client/`
- Live browsing of users, words, categories, translations, and parts of speech
- Auxiliary-service integration through a dedicated Study Packs menu
- Automated helper tests in `tests/test_client_helpers.py`

### Auxiliary service delivered

- Separate Flask service in `auxiliary_service/`
- Live fetches from the main API
- Derived study-pack endpoints:
  - `GET /study-pack/random`
  - `GET /study-pack/missing-translations`
  - `GET /study-pack/by-category`
- Automated tests in `tests/test_auxiliary_service.py`

## 2) Current architecture

```text
Terminal Client -> Main API
Terminal Client -> Study Pack Service
Study Pack Service -> Main API
```

The main API remains responsible for CRUD resources. The auxiliary service derives study-oriented responses from those resources.

## 3) Client evidence

### Implemented features

- Create and load users
- View dashboard totals
- Create, edit, delete, and browse words
- Create, edit, delete, and browse categories
- Create, edit, delete, and browse translations
- List parts of speech
- Open Study Packs and fetch:
  - random study pack
  - words missing translations
  - category-specific study pack

### Files to cite

- `client/main.py`
- `client/api_client.py`
- `client/study_pack_client.py`
- `client/storage.py`
- `client/README.md`
- `docs/deadline5/client_overview.md`
- `docs/deadline5/client_diagrams.md`

## 4) Auxiliary service evidence

### Implemented behavior

- Validates required query parameters
- Reads live words from `GET /words`
- Reads live categories from `GET /categories`
- Reads live translations from `GET /words/{word_id}/translations`
- Returns derived JSON responses for study workflows
- Maps upstream main-API failures into readable `502` responses

### Files to cite

- `auxiliary_service/app.py`
- `auxiliary_service/README.md`
- `docs/deadline5/auxiliary_service_design.md`

## 5) Submission check

### Client

- [x] Separate client exists
- [x] Client purpose and rationale documented
- [x] Resource and method mapping documented
- [x] Use-case diagram provided
- [x] Interface layout documented
- [x] Workflow documented
- [x] Multiple workflows implemented across several API resources
- [x] Error handling visible in code and demo paths
- [x] Client automated tests exist
- [x] Setup and run instructions exist
- [x] Quality-check command documented
- [x] Auxiliary-service integration exists

### Auxiliary service

- [x] Separate auxiliary service exists
- [x] Service purpose and justification documented
- [x] Endpoint design documented
- [x] Communication diagram documented
- [x] Request validation implemented
- [x] Live reads from the main API implemented
- [x] Automated tests exist
- [x] Setup and run instructions exist
- [x] Quality-check command documented

### Shared submission artifacts

- [x] Root README links the Deadline 5 materials
- [x] Demo checklist exists
- [x] OpenAPI documentation includes the new collection endpoints
- [x] Limitations are stated explicitly

## 6) Demo sequence

### Client demo

1. Start the main API.
2. Start the auxiliary service.
3. Run `python client/main.py`.
4. Create or load a user.
5. Create a category.
6. Create a word in that category.
7. Add a translation to the word.
8. Open Dashboard and show the live totals.
9. Open Study Packs and show:
   - a random pack
   - words missing translations
   - a category-specific pack
10. Trigger one handled error such as a duplicate user email.

### Auxiliary service demo

1. Call `/healthz`.
2. Call `/study-pack/random?user_id=<user_id>&count=2`.
3. Call `/study-pack/missing-translations?user_id=<user_id>`.
4. Call `/study-pack/by-category?user_id=<user_id>&category_id=<category_id>`.
5. Call one endpoint without `user_id` to show validation.

## 7) Remaining honest limitations

1. The client is a terminal interface rather than a graphical web UI.
2. The user list endpoint still requires the static bearer token used by the main API.
3. The auxiliary service currently derives responses on demand and does not persist a separate cache or database.

## 8) Final pre-submission checklist

- [x] `python -m pytest -q` passes
- [x] Main API starts locally
- [x] Auxiliary service starts locally
- [x] Client demo flow runs end-to-end
- [ ] Mermaid diagrams render in the final report format
- [ ] Screenshots or terminal captures are saved for the demo evidence
