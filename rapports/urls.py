from django.urls import path

from . import views

app_name = "rapports"

urlpatterns = [
    path("excel/", views.export_excel, name="excel"),
    path("pdf/", views.export_pdf, name="pdf"),
]
