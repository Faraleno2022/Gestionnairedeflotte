from django.contrib import admin

from .models import Article, MouvementStock


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ["code", "designation", "categorie", "stock_initial", "seuil_mini", "is_deleted"]
    list_filter = ["categorie", "is_deleted"]
    search_fields = ["code", "designation", "specification"]


@admin.register(MouvementStock)
class MouvementStockAdmin(admin.ModelAdmin):
    list_display = ["date", "article", "type", "quantite", "responsable", "is_deleted"]
    list_filter = ["type", "is_deleted"]
    search_fields = ["article__code", "article__designation", "motif", "responsable"]
    date_hierarchy = "date"
