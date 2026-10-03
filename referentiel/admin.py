from django.contrib import admin

from .models import CategorieRoues, Chauffeur, Engin, Vehicule


@admin.register(CategorieRoues)
class CategorieRouesAdmin(admin.ModelAdmin):
    list_display = ["libelle", "is_deleted", "updated_at"]
    search_fields = ["libelle"]


@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    list_display = ["nom_prenoms", "telephone", "actif", "is_deleted", "updated_at"]
    search_fields = ["nom_prenoms", "telephone"]
    list_filter = ["actif", "is_deleted"]


@admin.register(Vehicule)
class VehiculeAdmin(admin.ModelAdmin):
    list_display = [
        "immatriculation",
        "categorie_roues",
        "chauffeur_actuel",
        "actif",
        "is_deleted",
        "updated_at",
    ]
    search_fields = ["immatriculation"]
    list_filter = ["actif", "categorie_roues", "is_deleted"]


@admin.register(Engin)
class EnginAdmin(admin.ModelAdmin):
    list_display = ["nom", "type_engin", "actif", "is_deleted", "updated_at"]
    search_fields = ["nom"]
    list_filter = ["type_engin", "actif", "is_deleted"]
