from core.forms import BootstrapModelForm, DateInputFr

from .models import TrajetPorteChar


class TrajetPorteCharForm(BootstrapModelForm):
    class Meta:
        model = TrajetPorteChar
        fields = [
            "date", "engin", "point_depart", "point_arrivee",
            "km_depart", "km_arrivee", "montant_paye", "observation",
        ]
        widgets = {"date": DateInputFr()}
