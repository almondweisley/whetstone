"""Ingest Codex-generated candidates from disk and judge each one."""
import json
from pathlib import Path

from django.core.management.base import BaseCommand

from exercises.models import Candidate, Exercise, GenerationRun
from exercises.sandbox import judge


class Command(BaseCommand):
    help = "Judge candidate JSON files produced by Codex and publish survivors."

    def add_arguments(self, parser):
        parser.add_argument("directory", type=str)
        parser.add_argument("--topic", type=str, required=True)
        parser.add_argument("--difficulty", type=str, required=True)

    def handle(self, *args, **options):
        paths = sorted(Path(options["directory"]).glob("*.json"))
        if not paths:
            self.stderr.write("No candidate files found.")
            return

        run = GenerationRun.objects.create(
            topic=options["topic"],
            difficulty=options["difficulty"],
            requested_count=len(paths),
            status=GenerationRun.Status.RUNNING,
        )

        kept = 0
        for number, path in enumerate(paths, start=1):
            payload = json.loads(path.read_text(encoding="utf-8"))
            candidate = Candidate.objects.create(
                generation_run=run, attempt_number=number, **payload
            )
            verdict, reason = judge(candidate)
            candidate.verdict = verdict
            candidate.failure_reason = reason
            candidate.save(update_fields=["verdict", "failure_reason"])
            if verdict == Candidate.Verdict.PASS:
                Exercise.objects.create(winning_candidate=candidate)
                kept += 1
            self.stdout.write(f"  {path.name}: {verdict}")

        run.status = GenerationRun.Status.COMPLETED
        run.save(update_fields=["status"])
        self.stdout.write(
            self.style.SUCCESS(f"{len(paths)} generated, {kept} kept")
        )