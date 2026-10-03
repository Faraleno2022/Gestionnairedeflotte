from django.urls import path

from . import views

app_name = "pointage"

urlpatterns = [
    path("", views.grille, name="grille"),
    path("enregistrer/", views.enregistrer, name="enregistrer"),
    # Employés
    path("employes/", views.EmployeListe.as_view(), name="employe_liste"),
    path("employes/ajouter/", views.EmployeCreer.as_view(), name="employe_creer"),
    path("employes/<uuid:pk>/modifier/", views.EmployeModifier.as_view(), name="employe_modifier"),
    path("employes/<uuid:pk>/supprimer/", views.EmployeSupprimer.as_view(), name="employe_supprimer"),
]
