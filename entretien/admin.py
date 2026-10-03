from django.contrib import admin

from .models import Entretien


@admin.register(Entretien)
class EntretienAdmin(admin.ModelAdmin):
    list_display = ["date", "vehicule", "garage", "montant_ttc", "is_deleted", "updated_at"]
    list_filter = ["is_deleted", "vehicule"]
    search_fields = ["n_facture", "garage", "nature_operations"]
    date_hierarchy = "date"
