from django.urls import path

from . import api, views

app_name = "sync"

urlpatterns = [
    # API (serveur)
    path("ping/", api.PingView.as_view(), name="ping"),
    path("push/", api.PushView.as_view(), name="push"),
    path("pull/", api.PullView.as_view(), name="pull"),
    # Action interface (client) : bouton « Synchroniser »
    path("lancer/", views.lancer_synchro, name="lancer"),
]
