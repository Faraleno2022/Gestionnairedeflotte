from django.conf import settings

from core.permissions import peut_gerer_referentiel, peut_saisir


def app_context(request):
    """Variables disponibles dans tous les templates."""
    user = getattr(request, "user", None)
    return {
        "APP_NAME": "Gestion de Flotte CAB",
        "NODE_ROLE": settings.NODE_ROLE,
        "NODE_ID": settings.NODE_ID,
        "IS_SERVER": settings.NODE_ROLE == "server",
        "IS_CLIENT": settings.NODE_ROLE == "client",
        "PEUT_SAISIR": peut_saisir(user) if user else False,
        "PEUT_GERER_REFERENTIEL": peut_gerer_referentiel(user) if user else False,
    }
