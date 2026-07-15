# Frozen Flutter API contract

These endpoint paths, methods, request keys, response keys, and status codes are frozen for the Flutter frontend. Additive fields are permitted; renaming or removing fields requires a versioned `/api/v2/...` API.

## `POST /api/runs`

Request JSON: `{"topic": "sorting", "difficulty": "beginner", "count": 1}`. `count` is optional and defaults to `1`. A valid request returns `201` and `{"id": 42}` immediately; the run is queued for Celery. Invalid input returns `400` and `{"error": "..."}`.

## `GET /api/runs/<id>`

Returns `200` and `{"id", "topic", "difficulty", "requested_count", "status", "created_at", "candidates"}`. Each candidate has `id`, `attempt_number`, `problem_statement`, `verdict`, `failure_reason`, and `created_at`. Missing runs return `404` with `{"error": "run not found"}`.

## `GET /api/exercises`

Returns `200` and `{"exercises": [...]}`. Each published exercise has `id`, `problem_statement`, `published_at`, and `winning_candidate_id`.
