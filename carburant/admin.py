from django.contrib import admin

from .models import PleinCarburant


@admin.register(PleinCarburant)
class PleinCarburantAdmin(admin.ModelAdmin):
    list_display = ["date", "vehicule", "litres", "prix_litre", "montant", "is_deleted"]
    list_filter = ["is_deleted", "vehicule"]
    date_hierarchy = "date"
