from django.contrib import admin

from .models import Change, NodeState, SyncConflict


@admin.register(Change)
class ChangeAdmin(admin.ModelAdmin):
    list_display = ["seq", "model_label", "object_id", "is_deleted", "node", "ts"]
    list_filter = ["model_label", "is_deleted"]
    search_fields = ["object_id", "node"]


@admin.register(NodeState)
class NodeStateAdmin(admin.ModelAdmin):
    list_display = ["id", "last_pulled_seq", "last_push_at", "last_sync_ok"]


@admin.register(SyncConflict)
class SyncConflictAdmin(admin.ModelAdmin):
    list_display = ["created_at", "model_label", "object_id", "cote", "note"]
    list_filter = ["model_label", "cote"]
