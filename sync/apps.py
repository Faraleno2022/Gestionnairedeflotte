from django.apps import AppConfig


class SyncConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sync"
    verbose_name = "Synchronisation"

    def ready(self):
        from django.conf import settings

        # Le journal de réplication n'est tenu que par le hub central.
        if getattr(settings, "NODE_ROLE", "client") == "server":
            from .signals import enregistrer_signaux

            enregistrer_signaux()
