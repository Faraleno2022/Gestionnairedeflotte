"""
Crée les groupes de rôles et, si demandé, un compte administrateur.

Rôles :
- admin   : tout (référentiel + saisie + suppression) ;
- saisie  : création/modification des écritures ;
- lecture : consultation seule (tableaux de bord et listes).
"""
from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand

ROLES = ["admin", "saisie", "lecture"]


class Command(BaseCommand):
    help = "Initialise les groupes de rôles et un compte admin facultatif."

    def add_arguments(self, parser):
        parser.add_argument("--admin-user", default=None, help="Nom du compte admin à créer")
        parser.add_argument("--admin-pass", default=None, help="Mot de passe du compte admin")

    def handle(self, *args, **options):
        for nom in ROLES:
            _, cree = Group.objects.get_or_create(name=nom)
            self.stdout.write(f"Groupe {'créé' if cree else 'présent'} : {nom}")

        u, p = options["admin_user"], options["admin_pass"]
        if u and p:
            user, cree = User.objects.get_or_create(
                username=u, defaults={"is_staff": True, "is_superuser": True}
            )
            user.is_staff = True
            user.is_superuser = True
            user.set_password(p)
            user.save()
            user.groups.add(Group.objects.get(name="admin"))
            self.stdout.write(self.style.SUCCESS(f"Administrateur {'créé' if cree else 'mis à jour'} : {u}"))
