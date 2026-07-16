"""Seeding the database with verified exercises across the demo topic list."""
from django.core.management.base import BaseCommand

from exercises.models import GenerationRun
from exercises.tasks import generate_run

TOPICS = [
    ("list comprehensions", "beginner"),
    ("dictionary iteration", "beginner"),
    ("string manipulation", "beginner"),
    ("recursion", "intermediate"),
    ("sorting with custom keys", "intermediate"),
    ("set operations", "beginner"),
    ("generators and yield", "intermediate"),
    ("binary search", "intermediate"),
]


class Command(BaseCommand):
    help = "Generate and verify a seed corpus of published exercises."

    def add_arguments(self, parser):
        parser.add_argument("--per-topic", type=int, default=3)

    def handle(self, *args, **options):
        for topic, difficulty in TOPICS:
            run = GenerationRun.objects.create(
                topic = topic, difficulty = difficulty, requested_count = options["per_topic"]
            )    
            self.stdout.write(f"Run #{run.pk}: {topic} ({difficulty})")
            result = generate_run(run.pk)
            self.stdout.write(
                self.style.SUCCESS(
                    f"  {result['generated']} generated, {result['published']} kept"
                )
            )