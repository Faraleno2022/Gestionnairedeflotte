from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("comptes/", include("accounts.urls")),
    path("api/sync/", include("sync.urls")),
    path("referentiel/", include("referentiel.urls")),
    path("entretien/", include("entretien.urls")),
    path("carburant/", include("carburant.urls")),
    path("voyages/", include("voyages.urls")),
    path("poclain/", include("poclain.urls")),
    path("porte-char/", include("portechar.urls")),
    path("depenses/", include("depenses.urls")),
    path("pointage/", include("pointage.urls")),
    path("rapports/", include("rapports.urls")),
    path("", include("dashboard.urls")),
]
