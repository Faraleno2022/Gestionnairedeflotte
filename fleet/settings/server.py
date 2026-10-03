"""
Profil SERVEUR — hub central (source de vérité).

- PostgreSQL par défaut (recommandé pour 4 à 10 utilisateurs simultanés).
- Repli automatique sur SQLite si aucune configuration PostgreSQL n'est fournie
  (pratique pour tester le serveur en local sans installer PostgreSQL).
"""
import os

from .base import *  # noqa: F401,F403
from .base import BASE_DIR

NODE_ROLE = "server"

if os.environ.get("POSTGRES_DB"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ["POSTGRES_DB"],
            "USER": os.environ.get("POSTGRES_USER", "postgres"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
            "HOST": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        }
    }
else:
    # Repli SQLite : le serveur reste fonctionnel sans PostgreSQL.
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "data_server.sqlite3",
        }
    }
