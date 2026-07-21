"""The deliberately small, frozen JSON API consumed by the Flutter frontend."""
import json

from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_GET, require_http_methods

from .models import Candidate, Exercise, GenerationRun
from .services import start_generation


def _candidate_data(candidate):
    return {
        "id": candidate.pk,
        "attempt_number": candidate.attempt_number,
        "problem_statement": candidate.problem_statement,
        "verdict": candidate.verdict,
        "failure_reason": candidate.failure_reason,
        "created_at": candidate.created_at.isoformat(),
    }


@require_http_methods(["POST"])
def runs(request: HttpRequest):
    try:
        payload = json.loads(request.body)
        topic = payload["topic"].strip()
        difficulty = payload["difficulty"].strip()
        count = payload.get("count", 1)
        if not topic or not difficulty or not isinstance(count, int) or isinstance(count, bool) or count < 1:
            raise ValueError
    except (json.JSONDecodeError, KeyError, AttributeError, ValueError):
        return JsonResponse({"error": "topic and difficulty are required strings; count must be a positive integer."}, status=400)
    run = start_generation(topic=topic, difficulty=difficulty, count=count)
    return JsonResponse({"id": run.pk}, status=201)


@require_GET
def run_detail(request: HttpRequest, run_id: int):
    try:
        run = GenerationRun.objects.prefetch_related("candidates").get(pk=run_id)
    except GenerationRun.DoesNotExist:
        return JsonResponse({"error": "run not found"}, status=404)
    return JsonResponse({
        "id": run.pk, "topic": run.topic, "difficulty": run.difficulty,
        "requested_count": run.requested_count, "status": run.status,
        "created_at": run.created_at.isoformat(),
        "candidates": [_candidate_data(candidate) for candidate in run.candidates.all()],
    })


@require_GET
def exercises(request: HttpRequest):
    published = Exercise.objects.select_related("winning_candidate").order_by("-published_at")
    return JsonResponse({"exercises": [
        {
            "id": exercise.pk,
            "problem_statement": exercise.winning_candidate.problem_statement,
            "published_at": exercise.published_at.isoformat(),
            "winning_candidate_id": exercise.winning_candidate_id,
        }
        for exercise in published
    ]})


@require_GET
def discards(request: HttpRequest):
    failed = Candidate.objects.filter(
        verdict__in=[Candidate.Verdict.FAIL, Candidate.Verdict.ERROR]
    ).order_by("created_at")
    total = Candidate.objects.count()
    kept = Exercise.objects.count()
    return JsonResponse({
        "generated" : total,
        "kept" : kept,
        "discarded": total - kept,
        "discards": [
            {
                "id": c.pk,
                "topic": c.generation_run.topic,
                "problem_statement": c.problem_statement,
                "failure_reason": c.failure_reason,
            }
            for c in failed.select_related("generation_run")
        ],
    })   
