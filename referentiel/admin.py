from django.contrib import admin

from .models import CategorieRoues, Chauffeur, DocumentVehicule, Engin, Marque, Vehicule


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
        "marque",
        "capacite_tonnes",
        "numero_chassis",
        "actif",
        "is_deleted",
        "updated_at",
    ]
    search_fields = ["immatriculation", "numero_chassis"]
    list_filter = ["actif", "marque", "is_deleted"]


@admin.register(Marque)
class MarqueAdmin(admin.ModelAdmin):
    list_display = ["nom", "is_deleted", "updated_at"]
    search_fields = ["nom"]


@admin.register(DocumentVehicule)
class DocumentVehiculeAdmin(admin.ModelAdmin):
    list_display = ["vehicule", "type_document", "numero", "date_expiration", "is_deleted"]
    search_fields = ["vehicule__immatriculation", "numero"]
    list_filter = ["type_document", "is_deleted"]


@admin.register(Engin)
class EnginAdmin(admin.ModelAdmin):
    list_display = ["nom", "type_engin", "actif", "is_deleted", "updated_at"]
    search_fields = ["nom"]
    list_filter = ["type_engin", "actif", "is_deleted"]
