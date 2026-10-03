from django.contrib import admin

from .models import Employe, Pointage


@admin.register(Employe)
class EmployeAdmin(admin.ModelAdmin):
    list_display = ["nom_complet", "matricule", "fonction", "service", "actif", "is_deleted"]
    list_filter = ["actif", "service", "is_deleted"]
    search_fields = ["nom_complet", "matricule", "fonction", "service"]


@admin.register(Pointage)
class PointageAdmin(admin.ModelAdmin):
    list_display = ["employe", "date", "statut", "is_deleted", "updated_at"]
    list_filter = ["statut", "is_deleted"]
    search_fields = ["employe__nom_complet", "employe__matricule"]
    date_hierarchy = "date"
