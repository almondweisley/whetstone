from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("exercises", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="generationrun",
            name="status",
            field=models.CharField(
                choices=[("queued", "Queued"), ("running", "Running"), ("completed", "Completed"), ("failed", "Failed")],
                default="queued",
                max_length=16,
            ),
        ),
    ]
