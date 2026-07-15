from django.db import models


class GenerationRun(models.Model):
    """One invocation of the generate command."""

    class Status(models.TextChoices):
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    topic = models.CharField(max_length=255)
    difficulty = models.CharField(max_length=64)
    requested_count = models.PositiveIntegerField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.RUNNING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.topic} ({self.difficulty}) run #{self.pk}"


class Candidate(models.Model):
    """A generated solution, retained whether it passes or fails judging."""

    class Verdict(models.TextChoices):
        PENDING = "pending", "Pending"
        PASS = "pass", "Pass"
        FAIL = "fail", "Fail"
        ERROR = "error", "Error"

    generation_run = models.ForeignKey(GenerationRun, on_delete=models.CASCADE, related_name="candidates")
    problem_statement = models.TextField(blank=True)
    reference_solution = models.TextField(blank=True)
    test_source = models.TextField(blank=True)
    attempt_number = models.PositiveIntegerField(default=1)
    verdict = models.CharField(max_length=16, choices=Verdict.choices, default=Verdict.PENDING)
    failure_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Candidate #{self.pk} ({self.verdict})"


class Exercise(models.Model):
    """A published exercise, selected from a candidate that passed its tests."""

    winning_candidate = models.ForeignKey(Candidate, on_delete=models.PROTECT, related_name="published_exercises")
    published_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Exercise #{self.pk} from candidate #{self.winning_candidate_id}"

