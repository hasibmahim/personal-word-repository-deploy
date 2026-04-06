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

Main dependencies:
- Flask
- Flask-SQLAlchemy
- Flask-RESTful
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
https://github.com/sam2025202512/PersonalWordRepository
```

4. Let Rahti detect the `Dockerfile` and create the application.
5. Expose the service by creating a Route if one is not created automatically.
6. Open the generated URL and test:

```text
/
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

## Code Quality

Code quality was evaluated using PyLint, as required by the assignment.

Command used:

```bash
pylint wordrepo --disable=no-member,import-outside-toplevel,no-self-use

```

Final Pylint Score: 9.48/10

Remaining warnings and justifications:
- Trailing whitespace (C0303) > minor cosmetic issue; does not affect functionality
- Too few public methods (R0903) > Normal for SQLAlchemy models (primarily define fields and relationships)
- Trailing newlines (C0305) > extra blank line at the end of the code is harmless
- Cyclic imports (R0401) > expected in Flask applications using an application factory pattern (occur inside create_app(), so no runtime issues occur)
