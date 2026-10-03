from django.urls import path

from . import views

app_name = "stock"

urlpatterns = [
    path("", views.inventaire, name="inventaire"),
    path("synthese/", views.synthese, name="synthese"),
    # Articles
    path("articles/ajouter/", views.ArticleCreer.as_view(), name="article_creer"),
    path("articles/<uuid:pk>/modifier/", views.ArticleModifier.as_view(), name="article_modifier"),
    path("articles/<uuid:pk>/supprimer/", views.ArticleSupprimer.as_view(), name="article_supprimer"),
    # Mouvements
    path("mouvements/", views.MouvementListe.as_view(), name="mouvement_liste"),
    path("mouvements/ajouter/", views.MouvementCreer.as_view(), name="mouvement_creer"),
    path("mouvements/<uuid:pk>/modifier/", views.MouvementModifier.as_view(), name="mouvement_modifier"),
    path("mouvements/<uuid:pk>/supprimer/", views.MouvementSupprimer.as_view(), name="mouvement_supprimer"),
]
