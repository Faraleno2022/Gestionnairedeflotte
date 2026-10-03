from django.urls import reverse_lazy

from core.mixins import BaseCreer, BaseListe, BaseModifier, BaseSupprimer

from .forms import TrajetPorteCharForm
from .models import TrajetPorteChar


class TrajetListe(BaseListe):
    model = TrajetPorteChar
    titre = "Trajets porte-char"
    colonnes = [
        ("Date", "date"),
        ("Engin", "engin"),
        ("Départ", "point_depart"),
        ("Arrivée", "point_arrivee"),
        ("Montant payé", "montant_paye"),
    ]
    url_creer = "portechar:creer"
    url_modifier = "portechar:modifier"
    url_supprimer = "portechar:supprimer"

    def get_queryset(self):
        return super().get_queryset().select_related("engin")


class TrajetCreer(BaseCreer):
    model = TrajetPorteChar
    form_class = TrajetPorteCharForm
    success_url = reverse_lazy("portechar:liste")
    titre = "Ajouter un trajet"


class TrajetModifier(BaseModifier):
    model = TrajetPorteChar
    form_class = TrajetPorteCharForm
    success_url = reverse_lazy("portechar:liste")
    titre = "Modifier le trajet"


class TrajetSupprimer(BaseSupprimer):
    model = TrajetPorteChar
    success_url = reverse_lazy("portechar:liste")
