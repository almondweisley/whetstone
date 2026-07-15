# Whetstone

Whetstone is a small Django project that asks OpenAI for Python programming exercises, judges each reference solution with generated pytest tests, and publishes only candidates that pass. Failed candidates remain in the database as a discard log.

## Start it

1. Copy `.env.example` to `.env`, add an `OPENAI_API_KEY`, and export the values (for example, `set -a; source .env; set +a`).
2. Install Python dependencies: `python -m pip install -r requirements.txt`.
3. Start infrastructure: `docker compose up -d`.
4. Apply schema migrations: `python manage.py migrate`.
5. Generate an exercise: `python manage.py generate --topic sorting --difficulty beginner --count 1`.

The command needs a real API key. Its model is configurable with `OPENAI_MODEL` and defaults to `gpt-5-mini`.

> Safety note: generated code is untrusted. This learning project uses the requested subprocess and a 10-second timeout, but a production system should run the judge in a locked-down container or sandbox with CPU, memory, filesystem, and network limits.

## File guide

- `docker-compose.yml` starts PostgreSQL 16 and Redis 7 with persistent named volumes. PostgreSQL is the database Django uses; Redis is available for future queues/caching.
- `.env.example` documents configuration without committing secrets, and `.gitignore` prevents local secrets, virtual environments, and Python cache files from being committed.
- `requirements.txt` lists Django, the PostgreSQL driver, the OpenAI SDK, and pytest.
- `manage.py` is Django's command-line launcher. `whetstone/settings.py` registers the app and configures PostgreSQL from environment variables. `urls.py`, `wsgi.py`, and `asgi.py` are Django's web-routing and deployment entry points.
- `exercises/apps.py` registers the app. `models.py` contains the generation run, every candidate/discard, and each published exercise. `admin.py` makes them browsable in Django admin.
- `exercises/migrations/0001_initial.py` is the versioned database schema Django applies with `migrate`.
- `exercises/management/commands/generate.py` implements `python manage.py generate`: it calls the OpenAI Responses API with a strict JSON schema, writes `solution.py` and `test_solution.py` in a temporary directory, runs pytest with a 10-second limit, records the verdict, and creates an `Exercise` for every pass.
- Package marker files (`__init__.py`) tell Python which directories are importable; the management marker files let Django discover the `generate` command.
