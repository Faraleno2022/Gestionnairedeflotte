from core.forms import BootstrapModelForm, DateInputFr

from .models import PleinCarburant


class PleinCarburantForm(BootstrapModelForm):
    class Meta:
        model = PleinCarburant
        fields = [
            "date", "vehicule", "chauffeur", "litres",
            "prix_litre", "kilometrage", "n_bon", "observation",
        ]
        widgets = {"date": DateInputFr()}
