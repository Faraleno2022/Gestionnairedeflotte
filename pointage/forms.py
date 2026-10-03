from core.forms import BootstrapModelForm

from .models import Employe


class EmployeForm(BootstrapModelForm):
    class Meta:
        model = Employe
        fields = ["nom_complet", "matricule", "fonction", "service", "actif"]
