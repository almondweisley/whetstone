"""WSGI entry point, used by traditional Python web servers."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "whetstone.settings")
application = get_wsgi_application()

