"""Queue exercise generation and return immediately."""
import os

from django.core.management.base import BaseCommand, CommandError
from exercises.services import start_generation


class Command(BaseCommand):
    help = "Queue exercise generation; a Celery worker performs the OpenAI and Docker work."

    def add_arguments(self, parser):
        parser.add_argument("--topic", required=True, help="Subject of the programming exercises.")
        parser.add_argument("--difficulty", required=True, help="Difficulty label, e.g. beginner or intermediate.")
        parser.add_argument("--count", type=int, default=1, help="Number of exercises to request (default: 1).")

    def handle(self, *args, **options):
        if options["count"] < 1:
            raise CommandError("--count must be at least 1.")
        if not os.environ.get("OPENAI_API_KEY"):
            raise CommandError("OPENAI_API_KEY is required. Copy .env.example to .env and export its values.")

        run = start_generation(topic=options["topic"], difficulty=options["difficulty"], count=options["count"])
        self.stdout.write(self.style.SUCCESS(f"Run {run.pk} queued."))
