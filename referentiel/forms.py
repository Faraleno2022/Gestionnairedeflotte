from django import forms
from django.conf import settings

from .models import CategorieRoues, Chauffeur, DocumentVehicule, Engin, Marque, Vehicule


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


class MarqueForm(_BootstrapForm):
    class Meta:
        model = Marque
        fields = ["nom"]

    def clean_nom(self):
        return self.cleaned_data["nom"].strip().upper()


class ChauffeurForm(_BootstrapForm):
    class Meta:
        model = Chauffeur
        fields = ["nom_prenoms", "telephone", "actif"]


class VehiculeForm(_BootstrapForm):
    class Meta:
        model = Vehicule
        fields = [
            "immatriculation",
            "marque",
            "type_vehicule",
            "capacite_tonnes",
            "numero_chassis",
            "chauffeur_actuel",
            "actif",
        ]


class DocumentVehiculeForm(_BootstrapForm):
    class Meta:
        model = DocumentVehicule
        fields = [
            "vehicule",
            "type_document",
            "numero",
            "date_emission",
            "date_expiration",
            "fichier",
            "observations",
        ]
        widgets = {
            "date_emission": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "date_expiration": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            # Simple champ fichier : le lien « actuel » de Django pointerait
            # vers /media/, volontairement non servi publiquement.
            "fichier": forms.FileInput(
                attrs={"accept": ".pdf,.jpg,.jpeg,.png,.webp"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["vehicule"].queryset = Vehicule.objects.all()
        aide = f"PDF, JPG, PNG ou WEBP — {settings.DOCUMENTS_TAILLE_MAX_MO} Mo maximum."
        if self.instance.pk and self.instance.fichier:
            aide += " Laisser vide pour conserver le fichier actuel."
        self.fields["fichier"].help_text = aide

    def clean_fichier(self):
        fichier = self.cleaned_data.get("fichier")
        if fichier and getattr(fichier, "size", 0) > settings.DOCUMENTS_TAILLE_MAX_MO * 1024 * 1024:
            raise forms.ValidationError(
                f"Fichier trop volumineux (maximum {settings.DOCUMENTS_TAILLE_MAX_MO} Mo)."
            )
        return fichier

    def clean(self):
        data = super().clean()
        emission, expiration = data.get("date_emission"), data.get("date_expiration")
        if emission and expiration and expiration < emission:
            self.add_error("date_expiration", "La date d'expiration précède la date de délivrance.")
        return data


class EnginForm(_BootstrapForm):
    class Meta:
        model = Engin
        fields = ["nom", "type_engin", "actif"]
