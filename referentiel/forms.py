from django import forms

from .models import CategorieRoues, Chauffeur, Engin, Vehicule


class _BootstrapForm(forms.ModelForm):
    """Applique les classes Bootstrap aux widgets."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(widget, forms.Select):
                widget.attrs.setdefault("class", "form-select")
            else:
                widget.attrs.setdefault("class", "form-control")


class CategorieRouesForm(_BootstrapForm):
    class Meta:
        model = CategorieRoues
        fields = ["libelle"]


class ChauffeurForm(_BootstrapForm):
    class Meta:
        model = Chauffeur
        fields = ["nom_prenoms", "telephone", "actif"]


class VehiculeForm(_BootstrapForm):
    class Meta:
        model = Vehicule
        fields = [
            "immatriculation",
            "categorie_roues",
            "chauffeur_actuel",
            "type_vehicule",
            "actif",
        ]


class EnginForm(_BootstrapForm):
    class Meta:
        model = Engin
        fields = ["nom", "type_engin", "actif"]
