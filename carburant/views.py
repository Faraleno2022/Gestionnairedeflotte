from django.urls import reverse_lazy

from core.mixins import BaseCreer, BaseListe, BaseModifier, BaseSupprimer

from .forms import PleinCarburantForm
from .models import PleinCarburant


class PleinListe(BaseListe):
    model = PleinCarburant
    titre = "Pleins de carburant"
    colonnes = [
        ("Date", "date"),
        ("Véhicule", "vehicule"),
        ("Litres", "litres"),
        ("Prix/L", "prix_litre"),
        ("Montant", "montant"),
    ]
    url_creer = "carburant:creer"
    url_modifier = "carburant:modifier"
    url_supprimer = "carburant:supprimer"

    def get_queryset(self):
        return super().get_queryset().select_related("vehicule", "chauffeur")


class PleinCreer(BaseCreer):
    model = PleinCarburant
    form_class = PleinCarburantForm
    success_url = reverse_lazy("carburant:liste")
    titre = "Ajouter un plein"


class PleinModifier(BaseModifier):
    model = PleinCarburant
    form_class = PleinCarburantForm
    success_url = reverse_lazy("carburant:liste")
    titre = "Modifier le plein"


class PleinSupprimer(BaseSupprimer):
    model = PleinCarburant
    success_url = reverse_lazy("carburant:liste")
