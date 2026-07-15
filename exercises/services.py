"""Small shared service layer used by the command and frozen HTTP API."""
from .models import GenerationRun
from .tasks import generate_run


def start_generation(*, topic: str, difficulty: str, count: int) -> GenerationRun:
    run = GenerationRun.objects.create(topic=topic, difficulty=difficulty, requested_count=count)
    try:
        generate_run.delay(run.pk)
    except Exception:
        run.status = GenerationRun.Status.FAILED
        run.save(update_fields=["status"])
        raise
    return run
