from django.contrib import admin

from .models import Candidate, Exercise, GenerationRun


@admin.register(GenerationRun)
class GenerationRunAdmin(admin.ModelAdmin):
    list_display = ("id", "topic", "difficulty", "requested_count", "status", "created_at")
    list_filter = ("status", "difficulty")


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ("id", "generation_run", "attempt_number", "verdict", "created_at")
    list_filter = ("verdict",)


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("id", "winning_candidate", "published_at")

