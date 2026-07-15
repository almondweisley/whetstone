# Whetstone

Whetstone is a small Django project that asks OpenAI for Python programming exercises, judges each reference solution in a locked-down Docker container, and publishes only candidates that pass. Failed candidates remain in the database as a discard log.

## Start it

1. Copy `.env.example` to `.env`, add an `OPENAI_API_KEY`, and export the values (for example, `set -a; source .env; set +a`). This project maps PostgreSQL to host port `5433` to avoid a common local `5432` conflict.
2. Install Python dependencies: `python -m pip install -r requirements.txt`.
3. Start infrastructure: `docker compose up -d`.
4. Build the judge image: `docker compose --profile sandbox build sandbox`.
5. Apply schema migrations: `python manage.py migrate`.
6. Start a worker in a second terminal after exporting `.env`: `celery -A whetstone worker --loglevel=info`. The worker needs permission to run Docker (usually log out and back in after adding your user to the `docker` group).
7. Queue an exercise: `python manage.py generate --topic sorting --difficulty beginner --count 1`.

The command needs a real API key. Its model is configurable with `OPENAI_MODEL` and defaults to `gpt-5-mini`.

The command returns after enqueuing work. Celery reads Redis and makes the OpenAI call and Docker judging run in the background.

> Safety note: generated code is untrusted. The judge disables container networking, caps memory at 512 MB, uses a read-only root filesystem and code mount, removes Linux capabilities, limits processes, and kills the Docker command after 10 seconds. Production deployments should additionally use a dedicated Docker host/VM and restrictive daemon policy.

## Prove the sandbox blocks network access

After building the image, run this deliberately network-dependent test through the same Docker restrictions:

```bash
docker run --rm --network none --memory 512m --read-only --tmpfs /tmp:rw,noexec,nosuid,size=64m whetstone-sandbox:latest python -c "import socket; socket.create_connection(('1.1.1.1', 53), 2)"
```

It fails with a network-unreachable error. The production judge uses the same `--network none` flag in `exercises/sandbox.py`; a candidate that attempts network access fails pytest and is retained with its failure reason.

## Frozen API

The Flutter-facing endpoints are documented in `API_CONTRACT.md`: `POST /api/runs`, `GET /api/runs/<id>`, and `GET /api/exercises`. Set `CORS_ALLOWED_ORIGIN` to the one browser origin allowed to call them.

## File guide

- `docker-compose.yml` starts PostgreSQL 16 and Redis 7 with persistent named volumes, and defines the build target for the sandbox image. PostgreSQL is the database Django uses; Redis is Celery's broker.
- `.env.example` documents configuration without committing secrets, and `.gitignore` prevents local secrets, virtual environments, and Python cache files from being committed.
- `requirements.txt` lists Django, the PostgreSQL driver, the OpenAI SDK, pytest, Celery, and CORS middleware.
- `manage.py` is Django's command-line launcher. `whetstone/settings.py` registers the app, configures PostgreSQL and Celery/Redis, and reads the CORS origin. `whetstone/celery.py` creates Celery's application. `urls.py`, `wsgi.py`, and `asgi.py` are Django's web-routing and deployment entry points.
- `exercises/apps.py` registers the app. `models.py` contains the generation run, every candidate/discard, and each published exercise. `admin.py` makes them browsable in Django admin.
- `exercises/migrations/0001_initial.py` and `0002_generationrun_queued.py` are the versioned database schema Django applies with `migrate`; the latter adds the queued lifecycle state.
- `exercises/management/commands/generate.py` now only creates and queues a run. `services.py` shares that queueing behavior with the HTTP API, and `tasks.py` is the Celery worker's slow OpenAI/generation loop.
- `sandbox/Dockerfile` builds the `python:3.12-slim` judge image with pytest installed. `sandbox.py` writes the two generated files and invokes that image with the isolation restrictions. A Docker failure or timeout becomes a failed candidate instead of crashing the task.
- `views.py` implements the frozen JSON API; `API_CONTRACT.md` is the frontend-facing compatibility promise.
- Package marker files (`__init__.py`) tell Python which directories are importable; the management marker files let Django discover the `generate` command.
