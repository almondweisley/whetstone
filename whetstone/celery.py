"""Celery application configuration for background generation jobs."""
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "whetstone.settings")

app = Celery("whetstone")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
