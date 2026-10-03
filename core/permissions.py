"""
Droits d'accès par rôle (groupes Django : admin / saisie / lecture).

- admin   : tout (référentiel + écritures + suppression) ;
- saisie  : création/modification des écritures (pas le référentiel) ;
- lecture : consultation seule.

Un superutilisateur contourne toujours ces contrôles.
"""


def roles(user):
    if not user.is_authenticated:
        return set()
    return set(user.groups.values_list("name", flat=True))


def peut_saisir(user):
    """Peut créer/modifier des écritures (entretien, carburant, voyages, …)."""
    return bool(
        user.is_authenticated
        and (user.is_superuser or roles(user) & {"admin", "saisie"})
    )


def peut_gerer_referentiel(user):
    """Peut gérer le référentiel (véhicules, chauffeurs, catégories, engins)."""
    return bool(
        user.is_authenticated and (user.is_superuser or "admin" in roles(user))
    )
