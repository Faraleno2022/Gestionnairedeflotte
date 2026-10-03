from django.urls import path

from . import views

app_name = "entretien"

urlpatterns = [
    path("", views.EntretienListe.as_view(), name="liste"),
    path("ajouter/", views.EntretienCreer.as_view(), name="creer"),
    path("<uuid:pk>/modifier/", views.EntretienModifier.as_view(), name="modifier"),
    path("<uuid:pk>/supprimer/", views.EntretienSupprimer.as_view(), name="supprimer"),
]
