@echo off
REM ============================================================
REM  Lancement d'un POSTE NOMADE (fonctionne hors connexion)
REM  - Base de données SQLite locale (data_client.sqlite3)
REM  - Se synchronise avec le hub quand une connexion est là
REM ============================================================
cd /d "%~dp0"

set NODE_ROLE=client

REM --- Identité unique de CE poste (à personnaliser par machine) :
set NODE_ID=poste-01

REM --- Adresse du hub central (IP/nom du serveur sur le réseau) :
set SYNC_SERVER_URL=http://192.168.1.10:8000

REM --- Jeton de synchro fourni par le serveur :
REM     (obtenu via : python manage.py appairer_poste poste-01)
set SYNC_TOKEN=colle_ici_le_jeton_du_serveur

REM --- Intervalle de synchro automatique (secondes) :
set SYNC_INTERVAL_SECONDS=300

call .venv\Scripts\activate.bat

python manage.py migrate

REM Synchro automatique en tâche de fond (nouvelle fenêtre).
start "Synchro CAB" cmd /k "set NODE_ROLE=client&& set NODE_ID=%NODE_ID%&& set SYNC_SERVER_URL=%SYNC_SERVER_URL%&& set SYNC_TOKEN=%SYNC_TOKEN%&& .venv\Scripts\python.exe manage.py sync_daemon"

REM Application locale (accessible sur ce poste uniquement).
python -m waitress --listen=127.0.0.1:8000 fleet.wsgi:application
