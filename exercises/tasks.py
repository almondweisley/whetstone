"""Celery tasks that perform the slow OpenAI and Docker work off-request."""
import json
import os

from celery import shared_task
from openai import OpenAI

from .models import Candidate, Exercise, GenerationRun
from .sandbox import judge

EXERCISE_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "problem_statement": {"type": "string"},
        "reference_solution": {"type": "string"},
        "test_source": {"type": "string"},
    },
    "required": ["problem_statement", "reference_solution", "test_source"],
}

SYSTEM_PROMPT = """You write self-contained Python programming exercises. Return a JSON object only.
The reference_solution must be Python source defining solve(*args), with no Markdown fences.
The test_source must be pytest source defining tests and importing solve using `from solution import solve`.
Tests must call solve with ordinary Python values and must be deterministic, concise, and safe.
Do not read files, use the network, spawn processes, or depend on packages other than pytest."""


def _generate_candidate(client, run, attempt_number):
    try:
        response = client.responses.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-5-mini"),
            instructions=SYSTEM_PROMPT,
            input=f"Create one {run.difficulty} exercise about {run.topic}.",
            text={"format": {"type": "json_schema", "name": "exercise", "strict": True, "schema": EXERCISE_SCHEMA}},
        )
        payload = json.loads(response.output_text)
        return Candidate.objects.create(generation_run=run, attempt_number=attempt_number, **payload)
    except Exception as exc:
        return Candidate.objects.create(
            generation_run=run, attempt_number=attempt_number, verdict=Candidate.Verdict.ERROR,
            failure_reason=f"Generation failed: {exc}",
        )


@shared_task(bind=True)
def generate_run(self, run_id: int):
    """Generate every candidate for one persisted run, then judge and publish it."""
    run = GenerationRun.objects.get(pk=run_id)
    run.status = GenerationRun.Status.RUNNING
    run.save(update_fields=["status"])
    passed = 0
    try:
        client = OpenAI()
        for number in range(1, run.requested_count + 1):
            candidate = _generate_candidate(client, run, number)
            verdict, reason = judge(candidate)
            candidate.verdict = verdict
            candidate.failure_reason = reason
            candidate.save(update_fields=["verdict", "failure_reason"])
            if verdict == Candidate.Verdict.PASS:
                Exercise.objects.create(winning_candidate=candidate)
                passed += 1
        run.status = GenerationRun.Status.COMPLETED
        run.save(update_fields=["status"])
    except Exception:
        run.status = GenerationRun.Status.FAILED
        run.save(update_fields=["status"])
        raise
    return {"run_id": run.pk, "published": passed}
