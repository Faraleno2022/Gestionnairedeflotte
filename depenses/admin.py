from django.contrib import admin

from .models import AutreDepense


@admin.register(AutreDepense)
class AutreDepenseAdmin(admin.ModelAdmin):
    list_display = ["date", "designation", "prix_unitaire", "quantite", "montant", "is_deleted"]
    list_filter = ["is_deleted"]
    search_fields = ["designation"]
    date_hierarchy = "date"
