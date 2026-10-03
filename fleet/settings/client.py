"""
Profil CLIENT — poste/portable nomade.

- Base de données SQLite locale (fonctionne 100 % hors connexion).
- Se synchronise avec le hub central défini par SYNC_SERVER_URL.
"""
from .base import *  # noqa: F401,F403
from .base import BASE_DIR

NODE_ROLE = "client"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "data_client.sqlite3",
    }
}
