# Word Repository Terminal Client

This folder contains the Deadline 5 client implemented in Python with
`requests` and a simple terminal interface.

## Features

- create and load users
- browse live words for the active user
- list parts of speech
- create, edit, delete, and inspect words
- create, edit, delete, and inspect categories
- create, edit, delete, and inspect translations for a selected word
- display a small dashboard summary
- open study packs from the auxiliary service:
  - random study pack
  - missing-translations study pack
  - category study pack

## Notes

The client uses the live collection endpoints `GET /words` and
`GET /categories` for browsing. Local state is only used for saved users and
the active selected word between runs.

## Installation

From the project root:

```bash
python -m venv venv
source venv/bin/activate
pip install -r client/requirements.txt
```

If you are already using the same virtual environment for the API project, it is
enough to install:

```bash
pip install -r client/requirements.txt
```

## Running the client

Start the API first, then run:

```bash
python client/main.py
```

If you also want the Study Packs menu to work, start the auxiliary service too:

```bash
python auxiliary_service/app.py
```

## Quality checks

Install the shared development dependencies from the project root if you have
not already done so:

```bash
pip install -r requirements-dev.txt
```

Then run:

```bash
python -m pylint client auxiliary_service wordrepo --disable=missing-module-docstring,missing-function-docstring,missing-class-docstring,import-outside-toplevel,redefined-outer-name,too-many-public-methods,too-many-arguments,too-many-positional-arguments,too-many-locals,too-few-public-methods,trailing-whitespace,trailing-newlines,duplicate-code,cyclic-import
```

## Demo flow

1. Start the main API.
2. Launch the terminal client.
3. Create a user.
4. Create a category.
5. Create a word linked to that category.
6. Select the word and add a translation.
7. Open Dashboard to show the tracked totals.
8. Open Study Packs and show a random pack or category pack.
9. Trigger one handled API error, such as a duplicate user email.

## Configuration

Environment variables:

- `WORDREPO_API_BASE_URL`
  - default: `http://127.0.0.1:5000`
- `WORDREPO_AUX_SERVICE_BASE_URL`
  - default: `http://127.0.0.1:5050`
- `WORDREPO_CLIENT_STATE`
  - optional path for the local client state JSON file

## Local state

The client stores its local session state in:

```text
client/client_state.json
```

That file keeps:

- saved users
- active user ID
- active word ID

## Limitations

- The client is a terminal interface rather than a graphical web UI.
- The auxiliary Study Packs menu depends on the separate auxiliary service being
  started and reachable.
