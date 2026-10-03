"""
Alimentation du journal ``Change`` (SERVEUR uniquement).

Toute écriture sur un modèle synchronisé — qu'elle vienne de l'interface du
bureau ou d'un PUSH client — ajoute une ligne au journal, que les autres
postes tireront ensuite. Enregistré seulement quand NODE_ROLE == 'server'
(voir SyncConfig.ready).
"""
from django.apps import apps
from django.conf import settings
from django.db.models.signals import post_save

from .serializers import to_payload


def _journaliser(sender, instance, **kwargs):
    from .models import Change

    label = f"{instance._meta.app_label}.{instance._meta.object_name}"
    Change.objects.create(
        model_label=label,
        object_id=instance.pk,
        payload=to_payload(instance),
        is_deleted=getattr(instance, "is_deleted", False),
        node=getattr(instance, "origin_node", ""),
    )


def enregistrer_signaux():
    for label in settings.SYNC_MODELS:
        model = apps.get_model(label)
        post_save.connect(
            _journaliser,
            sender=model,
            dispatch_uid=f"journal_{label}",
        )
