"""Generate, judge, and publish programming exercises."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from openai import OpenAI

from exercises.models import Candidate, Exercise, GenerationRun


EXERCISE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
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


class Command(BaseCommand):
    help = "Generate exercises with OpenAI, judge them with pytest, and publish passing candidates."

    def add_arguments(self, parser):
        parser.add_argument("--topic", required=True, help="Subject of the programming exercises.")
        parser.add_argument("--difficulty", required=True, help="Difficulty label, e.g. beginner or intermediate.")
        parser.add_argument("--count", type=int, default=1, help="Number of exercises to request (default: 1).")

    def handle(self, *args, **options):
        if options["count"] < 1:
            raise CommandError("--count must be at least 1.")
        if not os.environ.get("OPENAI_API_KEY"):
            raise CommandError("OPENAI_API_KEY is required. Copy .env.example to .env and export its values.")

        run = GenerationRun.objects.create(
            topic=options["topic"], difficulty=options["difficulty"], requested_count=options["count"]
        )
        client = OpenAI()
        passed = 0
        try:
            for number in range(1, options["count"] + 1):
                candidate = self._generate_candidate(client, run, number)
                verdict, reason = self._judge(candidate)
                candidate.verdict = verdict
                candidate.failure_reason = reason
                candidate.save(update_fields=["verdict", "failure_reason"])
                if verdict == Candidate.Verdict.PASS:
                    Exercise.objects.create(winning_candidate=candidate)
                    passed += 1
                self.stdout.write(f"Candidate {candidate.pk}: {verdict}" + (f" — {reason}" if reason else ""))
            run.status = GenerationRun.Status.COMPLETED
            run.save(update_fields=["status"])
        except Exception:
            run.status = GenerationRun.Status.FAILED
            run.save(update_fields=["status"])
            raise

        self.stdout.write(self.style.SUCCESS(f"Run {run.pk} completed: {passed}/{options['count']} exercises published."))

    def _generate_candidate(self, client, run, attempt_number):
        prompt = f"Create one {run.difficulty} exercise about {run.topic}."
        try:
            response = client.responses.create(
                model=os.environ.get("OPENAI_MODEL", "gpt-5-mini"),
                instructions=SYSTEM_PROMPT,
                input=prompt,
                text={"format": {"type": "json_schema", "name": "exercise", "strict": True, "schema": EXERCISE_SCHEMA}},
            )
            payload = json.loads(response.output_text)
            return Candidate.objects.create(generation_run=run, attempt_number=attempt_number, **payload)
        except Exception as exc:
            # Keep failed API/format attempts in the same discard log as bad code.
            return Candidate.objects.create(
                generation_run=run, attempt_number=attempt_number, verdict=Candidate.Verdict.ERROR,
                failure_reason=f"Generation failed: {exc}",
            )

    def _judge(self, candidate):
        if candidate.verdict == Candidate.Verdict.ERROR:
            return candidate.verdict, candidate.failure_reason
        with tempfile.TemporaryDirectory(prefix="whetstone-judge-") as directory:
            workdir = Path(directory)
            (workdir / "solution.py").write_text(candidate.reference_solution, encoding="utf-8")
            (workdir / "test_solution.py").write_text(candidate.test_source, encoding="utf-8")
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pytest", "-q", "test_solution.py"],
                    cwd=workdir, text=True, capture_output=True, timeout=10, check=False,
                )
            except subprocess.TimeoutExpired:
                return Candidate.Verdict.FAIL, "Judge timed out after 10 seconds."

        if result.returncode == 0:
            return Candidate.Verdict.PASS, ""
        output = (result.stdout + "\n" + result.stderr).strip()
        return Candidate.Verdict.FAIL, output[-4000:] or f"pytest exited with status {result.returncode}."

