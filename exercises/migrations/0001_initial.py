# Generated as the initial schema for the exercises app.
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="GenerationRun",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("topic", models.CharField(max_length=255)),
                ("difficulty", models.CharField(max_length=64)),
                ("requested_count", models.PositiveIntegerField()),
                ("status", models.CharField(choices=[("queued", "Queued"), ("running", "Running"), ("completed", "Completed"), ("failed", "Failed")], default="queued", max_length=16)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Candidate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("problem_statement", models.TextField(blank=True)),
                ("reference_solution", models.TextField(blank=True)),
                ("test_source", models.TextField(blank=True)),
                ("attempt_number", models.PositiveIntegerField(default=1)),
                ("verdict", models.CharField(choices=[("pending", "Pending"), ("pass", "Pass"), ("fail", "Fail"), ("error", "Error")], default="pending", max_length=16)),
                ("failure_reason", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("generation_run", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="candidates", to="exercises.generationrun")),
            ],
        ),
        migrations.CreateModel(
            name="Exercise",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("published_at", models.DateTimeField(auto_now_add=True)),
                ("winning_candidate", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="published_exercises", to="exercises.candidate")),
            ],
        ),
    ]
