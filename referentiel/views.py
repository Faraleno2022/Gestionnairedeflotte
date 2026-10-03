from django.urls import reverse_lazy

from core.mixins import (
    BaseCreerReferentiel as BaseCreer,
    BaseListe,
    BaseModifierReferentiel as BaseModifier,
    BaseSupprimerReferentiel as BaseSupprimer,
)

from .forms import CategorieRouesForm, ChauffeurForm, EnginForm, VehiculeForm
from .models import CategorieRoues, Chauffeur, Engin, Vehicule


# --- Catégories de roues -------------------------------------------------
class CategorieListe(BaseListe):
    permission_edition = "referentiel"
    model = CategorieRoues
    titre = "Catégories de roues"
    colonnes = [("Libellé", "libelle")]
    url_creer = "referentiel:categorie_creer"
    url_modifier = "referentiel:categorie_modifier"
    url_supprimer = "referentiel:categorie_supprimer"


class CategorieCreer(BaseCreer):
    model = CategorieRoues
    form_class = CategorieRouesForm
    success_url = reverse_lazy("referentiel:categorie_liste")
    titre = "Ajouter une catégorie"


class CategorieModifier(BaseModifier):
    model = CategorieRoues
    form_class = CategorieRouesForm
    success_url = reverse_lazy("referentiel:categorie_liste")
    titre = "Modifier la catégorie"


class CategorieSupprimer(BaseSupprimer):
    model = CategorieRoues
    success_url = reverse_lazy("referentiel:categorie_liste")


# --- Chauffeurs ----------------------------------------------------------
class ChauffeurListe(BaseListe):
    permission_edition = "referentiel"
    model = Chauffeur
    titre = "Chauffeurs"
    colonnes = [
        ("Prénoms et Noms", "nom_prenoms"),
        ("Téléphone", "telephone"),
        ("Actif", "actif"),
    ]
    url_creer = "referentiel:chauffeur_creer"
    url_modifier = "referentiel:chauffeur_modifier"
    url_supprimer = "referentiel:chauffeur_supprimer"


class ChauffeurCreer(BaseCreer):
    model = Chauffeur
    form_class = ChauffeurForm
    success_url = reverse_lazy("referentiel:chauffeur_liste")
    titre = "Ajouter un chauffeur"


class ChauffeurModifier(BaseModifier):
    model = Chauffeur
    form_class = ChauffeurForm
    success_url = reverse_lazy("referentiel:chauffeur_liste")
    titre = "Modifier le chauffeur"


class ChauffeurSupprimer(BaseSupprimer):
    model = Chauffeur
    success_url = reverse_lazy("referentiel:chauffeur_liste")


# --- Véhicules -----------------------------------------------------------
class VehiculeListe(BaseListe):
    permission_edition = "referentiel"
    model = Vehicule
    titre = "Véhicules"
    colonnes = [
        ("Immatriculation", "immatriculation"),
        ("Catégorie", "categorie_roues"),
        ("Chauffeur", "chauffeur_actuel"),
        ("Type", "type_vehicule"),
        ("En service", "actif"),
    ]
    url_creer = "referentiel:vehicule_creer"
    url_modifier = "referentiel:vehicule_modifier"
    url_supprimer = "referentiel:vehicule_supprimer"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("categorie_roues", "chauffeur_actuel")
        )


class VehiculeCreer(BaseCreer):
    model = Vehicule
    form_class = VehiculeForm
    success_url = reverse_lazy("referentiel:vehicule_liste")
    titre = "Ajouter un véhicule"


class VehiculeModifier(BaseModifier):
    model = Vehicule
    form_class = VehiculeForm
    success_url = reverse_lazy("referentiel:vehicule_liste")
    titre = "Modifier le véhicule"


class VehiculeSupprimer(BaseSupprimer):
    model = Vehicule
    success_url = reverse_lazy("referentiel:vehicule_liste")


# --- Engins --------------------------------------------------------------
class EnginListe(BaseListe):
    permission_edition = "referentiel"
    model = Engin
    titre = "Engins"
    colonnes = [
        ("Nom", "nom"),
        ("Type", "get_type_engin_display"),
        ("En service", "actif"),
    ]
    url_creer = "referentiel:engin_creer"
    url_modifier = "referentiel:engin_modifier"
    url_supprimer = "referentiel:engin_supprimer"


class EnginCreer(BaseCreer):
    model = Engin
    form_class = EnginForm
    success_url = reverse_lazy("referentiel:engin_liste")
    titre = "Ajouter un engin"


class EnginModifier(BaseModifier):
    model = Engin
    form_class = EnginForm
    success_url = reverse_lazy("referentiel:engin_liste")
    titre = "Modifier l'engin"


class EnginSupprimer(BaseSupprimer):
    model = Engin
    success_url = reverse_lazy("referentiel:engin_liste")
