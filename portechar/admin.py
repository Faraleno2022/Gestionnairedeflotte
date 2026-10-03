from django.contrib import admin

from .models import TrajetPorteChar


@admin.register(TrajetPorteChar)
class TrajetPorteCharAdmin(admin.ModelAdmin):
    list_display = ["date", "engin", "point_depart", "point_arrivee", "montant_paye", "is_deleted"]
    list_filter = ["is_deleted"]
    date_hierarchy = "date"
