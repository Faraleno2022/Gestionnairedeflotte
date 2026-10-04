from django.urls import reverse_lazy

from core.mixins import BaseCreer, BaseListe, BaseModifier, BaseSupprimer

from .forms import ActiviteEnginForm
from .models import ActiviteEngin


class ActiviteListe(BaseListe):
    model = ActiviteEngin
    titre = "Activités Poclain"
    colonnes = [
        ("Date", "date"),
        ("Engin", "engin"),
        ("Roues", "categorie_roues"),
        ("Nb chargements", "nb_chargement"),
        ("Montant chargement", "montant_chargement"),
        ("Carburant (L)", "qte_carburant"),
        ("Montant carburant", "montant_carburant"),
    ]
    url_creer = "poclain:creer"
    url_modifier = "poclain:modifier"
    url_supprimer = "poclain:supprimer"

    def get_queryset(self):
        return super().get_queryset().select_related("engin", "categorie_roues")


class ActiviteCreer(BaseCreer):
    model = ActiviteEngin
    form_class = ActiviteEnginForm
    success_url = reverse_lazy("poclain:liste")
    titre = "Ajouter une activité Poclain"


class ActiviteModifier(BaseModifier):
    model = ActiviteEngin
    form_class = ActiviteEnginForm
    success_url = reverse_lazy("poclain:liste")
    titre = "Modifier l'activité"


class ActiviteSupprimer(BaseSupprimer):
    model = ActiviteEngin
    success_url = reverse_lazy("poclain:liste")
