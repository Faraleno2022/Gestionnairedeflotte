from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from .client import SyncError, synchroniser


@login_required
def lancer_synchro(request):
    """Bouton « Synchroniser » de l'interface (poste client)."""
    try:
        res = synchroniser()
        messages.success(
            request,
            f"Synchronisation réussie : {res.get('envoyes', 0)} envoyé(s), "
            f"{res.get('recus', 0)} reçu(s).",
        )
    except SyncError as exc:
        messages.warning(
            request,
            f"Synchronisation impossible pour le moment : {exc} "
            "Les données restent enregistrées localement et seront envoyées "
            "au retour de la connexion.",
        )
    return redirect(request.META.get("HTTP_REFERER", "dashboard:accueil"))
