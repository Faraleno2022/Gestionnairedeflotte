from django.contrib import admin

from .models import Voyage


@admin.register(Voyage)
class VoyageAdmin(admin.ModelAdmin):
    list_display = ["date", "vehicule", "chauffeur", "nb_voyage", "montant", "is_deleted"]
    list_filter = ["is_deleted", "vehicule"]
    date_hierarchy = "date"
