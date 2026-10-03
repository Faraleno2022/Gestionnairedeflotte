from django.urls import reverse_lazy

from core.mixins import BaseCreer, BaseListe, BaseModifier, BaseSupprimer

from .forms import EntretienForm
from .models import Entretien


class EntretienListe(BaseListe):
    model = Entretien
    titre = "Entretiens & Réparations"
    colonnes = [
        ("Date", "date"),
        ("Véhicule", "vehicule"),
        ("Garage", "garage"),
        ("Nature", "nature_operations"),
        ("Montant TTC", "montant_ttc"),
    ]
    url_creer = "entretien:creer"
    url_modifier = "entretien:modifier"
    url_supprimer = "entretien:supprimer"

    def get_queryset(self):
        return super().get_queryset().select_related("vehicule", "chauffeur")


class EntretienCreer(BaseCreer):
    model = Entretien
    form_class = EntretienForm
    success_url = reverse_lazy("entretien:liste")
    titre = "Ajouter un entretien"


class EntretienModifier(BaseModifier):
    model = Entretien
    form_class = EntretienForm
    success_url = reverse_lazy("entretien:liste")
    titre = "Modifier l'entretien"


class EntretienSupprimer(BaseSupprimer):
    model = Entretien
    success_url = reverse_lazy("entretien:liste")
