import os

from django.core.wsgi import get_wsgi_application

role = os.environ.get("NODE_ROLE", "client")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"fleet.settings.{role}")

application = get_wsgi_application()
