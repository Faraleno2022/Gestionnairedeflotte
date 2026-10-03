"""
Configuration commune (base) — Gestion de Flotte CAB.

Deux profils héritent de ce fichier :
- fleet.settings.client  -> poste nomade (SQLite, offline-first)
- fleet.settings.server  -> hub central (PostgreSQL, source de vérité)

Le profil est choisi par la variable d'environnement NODE_ROLE (voir manage.py).
"""
import os
import uuid
from pathlib import Path

# BASE_DIR = racine du projet (là où se trouve manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# --- Secret & debug -----------------------------------------------------
# En production, définir DJANGO_SECRET_KEY dans l'environnement.
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "dev-cab-flotte-CHANGER-EN-PRODUCTION-0123456789abcdef",
)
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = os.environ.get(
    "DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0"
).split(",")

# --- Identité du nœud ---------------------------------------------------
# Chaque installation (poste ou serveur) possède un identifiant stable,
# stocké dans un fichier à la racine. Il sert à tracer l'origine des
# données et à départager les conflits de synchronisation.
NODE_ROLE = os.environ.get("NODE_ROLE", "client")


def _get_or_create_node_id() -> str:
    id_file = BASE_DIR / ".node_id"
    if id_file.exists():
        return id_file.read_text(encoding="utf-8").strip()
    new_id = f"{NODE_ROLE}-{uuid.uuid4().hex[:12]}"
    try:
        id_file.write_text(new_id, encoding="utf-8")
    except OSError:
        pass
    return new_id


NODE_ID = os.environ.get("NODE_ID") or _get_or_create_node_id()

# URL du hub central, utilisée par le client pour se synchroniser.
SYNC_SERVER_URL = os.environ.get("SYNC_SERVER_URL", "http://127.0.0.1:8000")
# Jeton d'authentification du poste auprès du serveur (rempli après appairage).
SYNC_TOKEN = os.environ.get("SYNC_TOKEN", "")
# Périodicité de la synchro automatique (secondes) quand une connexion existe.
SYNC_INTERVAL_SECONDS = int(os.environ.get("SYNC_INTERVAL_SECONDS", "300"))

# --- Applications -------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    # Tiers
    "rest_framework",
    "rest_framework.authtoken",
    # Applications internes
    "core",
    "accounts",
    "referentiel",
    "entretien",
    "carburant",
    "voyages",
    "poclain",
    "portechar",
    "depenses",
    "dashboard",
    "rapports",
    "sync",
    "tools",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise sert les fichiers statiques en production (CSS/JS/images)
    # sans serveur web séparé. À placer juste après SecurityMiddleware.
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "fleet.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.app_context",
            ],
        },
    },
]

WSGI_APPLICATION = "fleet.wsgi.application"

# --- Validation des mots de passe --------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- Internationalisation (français) -----------------------------------
LANGUAGE_CODE = "fr"
TIME_ZONE = "Africa/Conakry"
USE_I18N = True
USE_TZ = True

# --- Fichiers statiques -------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Stockage des statiques : WhiteNoise (compression + cache-busting) en prod.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Origines de confiance pour le CSRF (formulaires POST en HTTPS).
# Ex. : DJANGO_CSRF_TRUSTED=https://votrecompte.pythonanywhere.com
CSRF_TRUSTED_ORIGINS = [
    o for o in os.environ.get("DJANGO_CSRF_TRUSTED", "").split(",") if o
]

# --- Authentification / redirections -----------------------------------
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "dashboard:accueil"
LOGOUT_REDIRECT_URL = "accounts:login"

# --- Django REST Framework (API de synchronisation) ---------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

# Modèles participant à la synchronisation, dans l'ordre de dépendance
# (les référentiels d'abord : ils sont référencés par les autres).
# Format : "app_label.ModelName".
SYNC_MODELS = [
    "referentiel.CategorieRoues",
    "referentiel.Chauffeur",
    "referentiel.Vehicule",
    "referentiel.Engin",
    "entretien.Entretien",
    "carburant.PleinCarburant",
    "voyages.Voyage",
    "poclain.ActiviteEngin",
    "portechar.TrajetPorteChar",
    "depenses.AutreDepense",
]
