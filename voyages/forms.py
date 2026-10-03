from core.forms import BootstrapModelForm, DateInputFr

from .models import Voyage


class VoyageForm(BootstrapModelForm):
    class Meta:
        model = Voyage
        fields = [
            "date", "vehicule", "chauffeur", "superviseur1", "superviseur2",
            "n_bon", "nb_voyage", "pu_voyage",
            "km_depart", "km_arrivee", "nb_heures",
        ]
        widgets = {"date": DateInputFr()}
