"""
(SERVEUR) Crée/associe un utilisateur de poste et renvoie son jeton d'API.

Le jeton obtenu est à renseigner côté client dans la variable
d'environnement SYNC_TOKEN (voir run_client.bat).
"""
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from rest_framework.authtoken.models import Token


class Command(BaseCommand):
    help = "Génère le jeton de synchronisation d'un poste (à exécuter sur le serveur)."

    def add_arguments(self, parser):
        parser.add_argument("nom_poste", help="Identifiant du poste, ex. poste-atelier-01")
        parser.add_argument("--mot-de-passe", default=None, help="Mot de passe du compte (facultatif).")

    def handle(self, *args, **options):
        nom = options["nom_poste"]
        user, cree = User.objects.get_or_create(
            username=nom, defaults={"is_staff": False}
        )
        if cree and options["mot_de_passe"]:
            user.set_password(options["mot_de_passe"])
            user.save()
        token, _ = Token.objects.get_or_create(user=user)
        etat = "créé" if cree else "existant"
        self.stdout.write(self.style.SUCCESS(f"Poste {etat} : {nom}"))
        self.stdout.write(f"SYNC_TOKEN={token.key}")
