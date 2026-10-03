from django.urls import path

from . import views

app_name = "carburant"

urlpatterns = [
    path("", views.PleinListe.as_view(), name="liste"),
    path("ajouter/", views.PleinCreer.as_view(), name="creer"),
    path("<uuid:pk>/modifier/", views.PleinModifier.as_view(), name="modifier"),
    path("<uuid:pk>/supprimer/", views.PleinSupprimer.as_view(), name="supprimer"),
]
