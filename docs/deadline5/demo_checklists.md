# Demo Checklists

## Client demo script

1. Start the API with `python -m flask --app wordrepo.api:create_app run`.
2. Start the client with `python client/main.py`.
3. Show the health check message on startup.
4. Create a new user.
5. Open the categories menu and create one category.
6. Open the words menu and create one word using an existing part-of-speech ID.
7. Select that word and open the translations menu.
8. Add one translation.
9. Open Dashboard and show the tracked totals.
10. Open Study Packs and show a random pack plus a category-specific pack.
11. Trigger one controlled error, for example trying to create the same email again.

## Auxiliary service demo script

1. Start the service with `python auxiliary_service/app.py`.
2. Open `/healthz` and show the `{"status": "ok"}` response.
3. Create or reuse one real user in the main API.
4. Call `/study-pack/random?user_id=<real_user_id>&count=2`.
5. Call `/study-pack/missing-translations?user_id=<real_user_id>`.
6. Call `/study-pack/by-category?user_id=<real_user_id>&category_id=<real_category_id>`.
7. Call `/study-pack/random` without `user_id` to show request validation.
8. Mention that the service is reading live data from the main API.

## Evidence capture checklist

- [ ] Screenshot or terminal capture of the client startup and health check
- [ ] Screenshot or terminal capture of user creation
- [ ] Screenshot or terminal capture of word plus translation creation
- [ ] Screenshot or terminal capture of dashboard totals
- [ ] Screenshot or terminal capture of one handled client-side API error
- [ ] Screenshot or terminal capture of auxiliary `/healthz`
- [ ] Screenshot or terminal capture of one successful auxiliary study-pack response
- [ ] Screenshot or terminal capture of one auxiliary `400` validation response
