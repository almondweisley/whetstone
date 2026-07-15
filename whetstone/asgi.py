"""ASGI entry point, used by asynchronous production servers."""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "whetstone.settings")
application = get_asgi_application()

