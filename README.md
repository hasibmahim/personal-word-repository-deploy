# PWP SPRING 2026
# PERSONAL WORD REPOSITORY
# Group information
* Student 1. Sami Häkkilä - sami.hakkila@student.oulu.fi
* Student 2. Saara Laasonen - Saara.Laasonen@student.oulu.fi
* Student 3. Syed Mahim - Syed.Mahim@student.oulu.fi


This project implements a RESTful API for storing, categorizing and translating personal vocabulary. The repository includes full documentation on setup, database initialization, running the API, and code quality verification.

---

## Technologies

- Python 3
- Flask
- Flask-SQLAlchemy
- Flask-RESTful
- SQLite (default database)
- PyLint (code quality)

---

## Dependencies

Project dependencies are listed in `requirements.txt`.
Developer and testing dependencies are listed in `requirements-dev.txt`.

Main dependencies:
- Flask
- Flask-SQLAlchemy
- Flask-RESTful
- jsonschema
---

## Running the project

Run all commands from the project root directory, where `README.md`, `init_db.py`, and the `wordrepo/` folder are located.

### Windows (PowerShell)

1. Create a virtual environment:

```powershell
python -m venv venv
```

2. Activate the virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

4. Initialize the database:

```powershell
python init_db.py
```

5. Start the Flask API:

```powershell
python -m flask --app wordrepo.api:create_app run
```

### Linux / macOS (Bash)

1. Create a virtual environment:

```bash
python3 -m venv venv
```

2. Activate the virtual environment:

```bash
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

4. Initialize the database:

```bash
python init_db.py
```

5. Start the Flask API:

```bash
python -m flask --app wordrepo.api:create_app run
```

## Option: Running with Docker (Docker Compose)

The project includes a `Dockerfile` and `docker-compose.yml` for containerized usage.

Build and start the API:

```bash
docker compose up --build
```

The API will be available at:

```text
http://127.0.0.1:5000/
```

The SQLite database is stored in the local `instance/` folder and mounted into the container, so data persists between restarts.

Stop the service with:

```bash
docker compose down
```

## Quick Publish On Rahti

The fastest way to publish this API with the available university services is to use `Rahti Container Cloud`.

1. Log in to Rahti and create a project.
2. Click the `+` button in the web console and choose `Import from Git`.
3. Use this repository URL:

```text
https://github.com/hasibmahim/personal-word-repository-deploy.git
```

4. Let Rahti detect the `Dockerfile` and create the application.
5. Expose the service by creating a Route if one is not created automatically.
6. Open the generated URL and test:

```text
/healthz
/docs
/openapi.yaml
```

Note: the current deployment uses SQLite inside the container. That is fine for a quick publish/demo, but the data is not durable unless you attach persistent storage or move the database to a managed service such as Pukki.

## Best Persistent Deployment

For a persistent deployment on CSC services, the recommended setup is:

- `Rahti` for running the API container
- `Pukki` for a managed PostgreSQL database
- `Gunicorn` as the Python WSGI application server
- `NGINX` as the web server and reverse proxy
- `Supervisor` for process control inside the container

The application already supports a database URL through the `SQLALCHEMY_DATABASE_URI` environment variable. In Rahti, set it to a PostgreSQL connection string, for example:

```text
postgresql+psycopg://USERNAME:PASSWORD@HOSTNAME:5432/DATABASE_NAME
```

With this setup, application data is stored outside the container and remains available across pod restarts and redeployments.

## Deployment Architecture

Recommended production-style deployment:

- Public client -> `HTTPS` -> `Rahti Route`
- `Rahti Route` -> `HTTP` -> `NGINX` inside the container
- `NGINX` -> `HTTP` -> `Gunicorn`
- `Gunicorn` -> `SQLAlchemy` -> `PostgreSQL` in `Pukki`

This setup gives a clear separation of concerns:

- `NGINX` handles incoming HTTP traffic and reverse proxies requests
- `Gunicorn` runs the Flask application as a proper WSGI application server
- `Supervisor` keeps both processes managed in the same container
- `Pukki` stores the persistent database outside the application container


## API entry point

After starting the server, the API is available at:

```text
http://127.0.0.1:5000/
```

## API documentation

The repository includes an OpenAPI 3.0 specification at `docs/openapi.yaml`.

When the server is running, the documentation is available live at:

```text
http://127.0.0.1:5000/docs
```

The raw OpenAPI file is available at:

```text
http://127.0.0.1:5000/openapi.yaml
```

## Running Tests

Run the automated tests from the project root:

```bash
python -m pytest -q
```

## Coverage Report

Generate the test coverage report with:

```bash
python -m pytest --cov=wordrepo --cov-report=term-missing
```

This command shows line-by-line coverage information in the terminal so the API implementation and tested branches can be demonstrated during review.

## Deadline 5 Client

The Deadline 5 client now lives under `client/` in two forms:
- `client/web.py` for the browser-based GUI
- [client/main.py](/workspaces/PersonalWordRepository/client/main.py) for the original terminal client

Install the client dependency:

```bash
pip install -r client/requirements.txt
```

Then run the GUI client after the API is running:

```bash
python client/web.py
```

The GUI is available at:

```text
http://127.0.0.1:8001
```

You can still run the terminal client with:

```bash
python client/main.py
```

For a separate cloud deployment of the GUI client, the repository includes:

```text
client/Dockerfile
```

That file is intended for importing the same repository into Rahti as a second
application with `WORDREPO_API_BASE_URL` pointing at the online API route.

For the integrated study-pack flows, also run:

```bash
python auxiliary_service/app.py
```

For a separate cloud deployment of the auxiliary service, the repository
includes:

```text
auxiliary_service/Dockerfile
```

That deployment should set:

```text
MAIN_API_BASE_URL=https://your-online-api-route
```

The client stores a small local state file so it can remember saved users and
the active selected word between runs.

Additional Deadline 5 submission material lives in:

- `DEADLINE5_PLAN.md`
- `docs/deadline5/README.md`
- `docs/deadline5/client_overview.md`
- `docs/deadline5/client_diagrams.md`
- `docs/deadline5/auxiliary_service_design.md`
- `docs/deadline5/demo_checklists.md`

## Code Quality

Code quality was evaluated using PyLint, as required by the assignment.

Command used:

```bash
python -m pylint client auxiliary_service wordrepo \
  --disable=missing-module-docstring,missing-function-docstring,missing-class-docstring,import-outside-toplevel,redefined-outer-name,too-many-public-methods,too-many-arguments,too-many-positional-arguments,too-many-locals,too-few-public-methods,trailing-whitespace,trailing-newlines,duplicate-code,cyclic-import

```

Final Pylint Score: 10.00/10
