from django.urls import reverse_lazy

from core.mixins import BaseCreer, BaseListe, BaseModifier, BaseSupprimer

from .forms import AutreDepenseForm
from .models import AutreDepense


class DepenseListe(BaseListe):
    model = AutreDepense
    titre = "Autres dépenses"
    colonnes = [
        ("Date", "date"),
        ("Désignation", "designation"),
        ("PU", "prix_unitaire"),
        ("Quantité", "quantite"),
        ("Montant", "montant"),
    ]
    url_creer = "depenses:creer"
    url_modifier = "depenses:modifier"
    url_supprimer = "depenses:supprimer"


class DepenseCreer(BaseCreer):
    model = AutreDepense
    form_class = AutreDepenseForm
    success_url = reverse_lazy("depenses:liste")
    titre = "Ajouter une dépense"


class DepenseModifier(BaseModifier):
    model = AutreDepense
    form_class = AutreDepenseForm
    success_url = reverse_lazy("depenses:liste")
    titre = "Modifier la dépense"


class DepenseSupprimer(BaseSupprimer):
    model = AutreDepense
    success_url = reverse_lazy("depenses:liste")
