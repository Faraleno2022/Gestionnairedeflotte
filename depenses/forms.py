from core.forms import BootstrapModelForm, DateInputFr

from .models import AutreDepense


class AutreDepenseForm(BootstrapModelForm):
    class Meta:
        model = AutreDepense
        fields = ["date", "designation", "prix_unitaire", "quantite", "observation"]
        widgets = {"date": DateInputFr()}
