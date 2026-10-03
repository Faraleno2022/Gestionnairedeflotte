#!/usr/bin/env python
"""Utilitaire de ligne de commande Django pour la Gestion de Flotte CAB."""
import os
import sys


def main():
    # Rôle du nœud : 'server' (hub central) ou 'client' (poste nomade).
    # Défini par la variable d'environnement NODE_ROLE, 'client' par défaut.
    role = os.environ.get("NODE_ROLE", "client")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"fleet.settings.{role}")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django est introuvable. Activez l'environnement virtuel "
            "(.venv) et installez les dépendances : pip install -r requirements.txt"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
