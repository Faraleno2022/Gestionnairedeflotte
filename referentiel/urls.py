from django.urls import path

from . import views

app_name = "referentiel"

urlpatterns = [
    # Catégories de roues
    path("categories/", views.CategorieListe.as_view(), name="categorie_liste"),
    path("categories/ajouter/", views.CategorieCreer.as_view(), name="categorie_creer"),
    path("categories/<uuid:pk>/modifier/", views.CategorieModifier.as_view(), name="categorie_modifier"),
    path("categories/<uuid:pk>/supprimer/", views.CategorieSupprimer.as_view(), name="categorie_supprimer"),
    # Marques
    path("marques/", views.MarqueListe.as_view(), name="marque_liste"),
    path("marques/ajouter/", views.MarqueCreer.as_view(), name="marque_creer"),
    path("marques/<uuid:pk>/modifier/", views.MarqueModifier.as_view(), name="marque_modifier"),
    path("marques/<uuid:pk>/supprimer/", views.MarqueSupprimer.as_view(), name="marque_supprimer"),
    # Chauffeurs
    path("chauffeurs/", views.ChauffeurListe.as_view(), name="chauffeur_liste"),
    path("chauffeurs/ajouter/", views.ChauffeurCreer.as_view(), name="chauffeur_creer"),
    path("chauffeurs/<uuid:pk>/modifier/", views.ChauffeurModifier.as_view(), name="chauffeur_modifier"),
    path("chauffeurs/<uuid:pk>/supprimer/", views.ChauffeurSupprimer.as_view(), name="chauffeur_supprimer"),
    # Véhicules
    path("vehicules/", views.VehiculeListe.as_view(), name="vehicule_liste"),
    path("vehicules/ajouter/", views.VehiculeCreer.as_view(), name="vehicule_creer"),
    path("vehicules/<uuid:pk>/", views.vehicule_detail, name="vehicule_detail"),
    path("vehicules/<uuid:pk>/modifier/", views.VehiculeModifier.as_view(), name="vehicule_modifier"),
    path("vehicules/<uuid:pk>/supprimer/", views.VehiculeSupprimer.as_view(), name="vehicule_supprimer"),
    # Documents des véhicules
    path("documents/", views.document_liste, name="document_liste"),
    path("documents/ajouter/", views.DocumentCreer.as_view(), name="document_creer"),
    path("documents/<uuid:pk>/modifier/", views.DocumentModifier.as_view(), name="document_modifier"),
    path("documents/<uuid:pk>/supprimer/", views.DocumentSupprimer.as_view(), name="document_supprimer"),
    path("documents/<uuid:pk>/fichier/", views.document_fichier, name="document_fichier"),
    # Engins
    path("engins/", views.EnginListe.as_view(), name="engin_liste"),
    path("engins/ajouter/", views.EnginCreer.as_view(), name="engin_creer"),
    path("engins/<uuid:pk>/modifier/", views.EnginModifier.as_view(), name="engin_modifier"),
    path("engins/<uuid:pk>/supprimer/", views.EnginSupprimer.as_view(), name="engin_supprimer"),
]
