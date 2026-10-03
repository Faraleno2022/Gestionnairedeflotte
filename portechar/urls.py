from django.urls import path

from . import views

app_name = "portechar"

urlpatterns = [
    path("", views.TrajetListe.as_view(), name="liste"),
    path("ajouter/", views.TrajetCreer.as_view(), name="creer"),
    path("<uuid:pk>/modifier/", views.TrajetModifier.as_view(), name="modifier"),
    path("<uuid:pk>/supprimer/", views.TrajetSupprimer.as_view(), name="supprimer"),
]
