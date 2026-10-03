from django import forms

from core.forms import BootstrapModelForm, DateInputFr

from .models import Entretien


class EntretienForm(BootstrapModelForm):
    class Meta:
        model = Entretien
        fields = [
            "date", "vehicule", "chauffeur", "n_facture",
            "km_depart", "km_arrivee", "garage",
            "nature_operations", "montant_ttc", "observation",
        ]
        widgets = {
            "date": DateInputFr(),
            "nature_operations": forms.Textarea(attrs={"rows": 2}),
        }
