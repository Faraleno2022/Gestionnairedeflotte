from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.accueil, name="accueil"),
    path("analyses/", views.analyses, name="analyses"),
]
