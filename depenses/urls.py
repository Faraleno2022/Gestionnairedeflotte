from django.urls import path

from . import views

app_name = "depenses"

urlpatterns = [
    path("", views.DepenseListe.as_view(), name="liste"),
    path("ajouter/", views.DepenseCreer.as_view(), name="creer"),
    path("<uuid:pk>/modifier/", views.DepenseModifier.as_view(), name="modifier"),
    path("<uuid:pk>/supprimer/", views.DepenseSupprimer.as_view(), name="supprimer"),
]
