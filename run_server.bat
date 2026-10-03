@echo off
REM ============================================================
REM  Lancement du HUB CENTRAL (serveur de synchronisation)
REM  Toutes les données des postes remontent ici.
REM ============================================================
cd /d "%~dp0"

set NODE_ROLE=server

REM --- PostgreSQL (recommandé). Décommentez et renseignez :
REM set POSTGRES_DB=flotte
REM set POSTGRES_USER=postgres
REM set POSTGRES_PASSWORD=motdepasse
REM set POSTGRES_HOST=127.0.0.1
REM set POSTGRES_PORT=5432
REM (Sans ces variables, le serveur utilise SQLite : data_server.sqlite3)

REM --- Clé secrète en production (à personnaliser) :
REM set DJANGO_SECRET_KEY=changez-moi-en-production

call .venv\Scripts\activate.bat

python manage.py migrate
python manage.py collectstatic --noinput

REM Serveur de production (waitress). Accessible sur le réseau local (0.0.0.0).
REM Port 8010 (le 8000 est déjà utilisé par un autre logiciel sur ce PC).
python -m waitress --listen=0.0.0.0:8010 fleet.wsgi:application
