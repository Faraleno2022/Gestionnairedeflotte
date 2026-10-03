from django.contrib import admin

from .models import ActiviteEngin


@admin.register(ActiviteEngin)
class ActiviteEnginAdmin(admin.ModelAdmin):
    list_display = ["date", "engin", "nb_chargement", "montant_chargement", "montant_carburant", "is_deleted"]
    list_filter = ["is_deleted", "engin"]
    date_hierarchy = "date"
