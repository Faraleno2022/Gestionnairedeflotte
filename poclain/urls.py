from django.urls import path

from . import views

app_name = "poclain"

urlpatterns = [
    path("", views.ActiviteListe.as_view(), name="liste"),
    path("ajouter/", views.ActiviteCreer.as_view(), name="creer"),
    path("<uuid:pk>/modifier/", views.ActiviteModifier.as_view(), name="modifier"),
    path("<uuid:pk>/supprimer/", views.ActiviteSupprimer.as_view(), name="supprimer"),
]
