from core.forms import BootstrapModelForm, DateInputFr

from .models import ActiviteEngin


class ActiviteEnginForm(BootstrapModelForm):
    class Meta:
        model = ActiviteEngin
        fields = [
            "date", "engin", "categorie_roues", "nb_chargement", "pu_chargement",
            "qte_carburant", "prix_litre", "observation",
        ]
        widgets = {"date": DateInputFr()}
