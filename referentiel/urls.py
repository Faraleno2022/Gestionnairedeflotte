from django.urls import path

from . import views

app_name = "referentiel"

urlpatterns = [
    # Catégories de roues
    path("categories/", views.CategorieListe.as_view(), name="categorie_liste"),
    path("categories/ajouter/", views.CategorieCreer.as_view(), name="categorie_creer"),
    path("categories/<uuid:pk>/modifier/", views.CategorieModifier.as_view(), name="categorie_modifier"),
    path("categories/<uuid:pk>/supprimer/", views.CategorieSupprimer.as_view(), name="categorie_supprimer"),
    # Chauffeurs
    path("chauffeurs/", views.ChauffeurListe.as_view(), name="chauffeur_liste"),
    path("chauffeurs/ajouter/", views.ChauffeurCreer.as_view(), name="chauffeur_creer"),
    path("chauffeurs/<uuid:pk>/modifier/", views.ChauffeurModifier.as_view(), name="chauffeur_modifier"),
    path("chauffeurs/<uuid:pk>/supprimer/", views.ChauffeurSupprimer.as_view(), name="chauffeur_supprimer"),
    # Véhicules
    path("vehicules/", views.VehiculeListe.as_view(), name="vehicule_liste"),
    path("vehicules/ajouter/", views.VehiculeCreer.as_view(), name="vehicule_creer"),
    path("vehicules/<uuid:pk>/modifier/", views.VehiculeModifier.as_view(), name="vehicule_modifier"),
    path("vehicules/<uuid:pk>/supprimer/", views.VehiculeSupprimer.as_view(), name="vehicule_supprimer"),
    # Engins
    path("engins/", views.EnginListe.as_view(), name="engin_liste"),
    path("engins/ajouter/", views.EnginCreer.as_view(), name="engin_creer"),
    path("engins/<uuid:pk>/modifier/", views.EnginModifier.as_view(), name="engin_modifier"),
    path("engins/<uuid:pk>/supprimer/", views.EnginSupprimer.as_view(), name="engin_supprimer"),
]
