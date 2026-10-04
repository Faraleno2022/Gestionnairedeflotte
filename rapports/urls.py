from django.urls import path

from . import views

app_name = "rapports"

urlpatterns = [
    path("excel/", views.export_excel, name="excel"),
    path("pdf/", views.export_pdf, name="pdf"),
    path("mensuel/", views.rapport_mensuel, name="mensuel"),
    path("charges-entretien/", views.charges_entretien, name="charges_entretien"),
    path("carburant/", views.consommation_carburant, name="carburant"),
    path("poclain/", views.analyse_poclain, name="poclain"),
]
