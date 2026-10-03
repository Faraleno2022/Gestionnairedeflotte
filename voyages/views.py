from django.urls import reverse_lazy

from core.mixins import BaseCreer, BaseListe, BaseModifier, BaseSupprimer

from .forms import VoyageForm
from .models import Voyage


class VoyageListe(BaseListe):
    model = Voyage
    titre = "Voyages"
    colonnes = [
        ("Date", "date"),
        ("Véhicule", "vehicule"),
        ("Chauffeur", "chauffeur"),
        ("Nb voyages", "nb_voyage"),
        ("Montant", "montant"),
    ]
    url_creer = "voyages:creer"
    url_modifier = "voyages:modifier"
    url_supprimer = "voyages:supprimer"

    def get_queryset(self):
        return super().get_queryset().select_related("vehicule", "chauffeur")


class VoyageCreer(BaseCreer):
    model = Voyage
    form_class = VoyageForm
    success_url = reverse_lazy("voyages:liste")
    titre = "Ajouter un voyage"


class VoyageModifier(BaseModifier):
    model = Voyage
    form_class = VoyageForm
    success_url = reverse_lazy("voyages:liste")
    titre = "Modifier le voyage"


class VoyageSupprimer(BaseSupprimer):
    model = Voyage
    success_url = reverse_lazy("voyages:liste")
