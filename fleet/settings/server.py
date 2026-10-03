"""
Profil SERVEUR — hub central (source de vérité).

Base de données choisie selon les variables d'environnement, par priorité :
1. MySQL        si MYSQL_DB est défini      (recommandé sur PythonAnywhere) ;
2. PostgreSQL   si POSTGRES_DB est défini ;
3. SQLite       sinon (repli, pour tester en local sans serveur de BDD).
"""
import os

from .base import *  # noqa: F401,F403
from .base import BASE_DIR

NODE_ROLE = "server"

if os.environ.get("MYSQL_DB"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.environ["MYSQL_DB"],
            "USER": os.environ.get("MYSQL_USER", ""),
            "PASSWORD": os.environ.get("MYSQL_PASSWORD", ""),
            "HOST": os.environ.get("MYSQL_HOST", "127.0.0.1"),
            "PORT": os.environ.get("MYSQL_PORT", "3306"),
            "OPTIONS": {
                # utf8mb4 : accents français et emojis pris en charge.
                "charset": "utf8mb4",
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            },
            "CONN_MAX_AGE": 60,
        }
    }
elif os.environ.get("POSTGRES_DB"):
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
    # Repli SQLite : le serveur reste fonctionnel sans serveur de BDD.
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "data_server.sqlite3",
        }
    }
