from django.urls import path

from . import views

app_name = "voyages"

urlpatterns = [
    path("", views.VoyageListe.as_view(), name="liste"),
    path("ajouter/", views.VoyageCreer.as_view(), name="creer"),
    path("<uuid:pk>/modifier/", views.VoyageModifier.as_view(), name="modifier"),
    path("<uuid:pk>/supprimer/", views.VoyageSupprimer.as_view(), name="supprimer"),
]
