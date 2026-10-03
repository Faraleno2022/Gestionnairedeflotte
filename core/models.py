"""
Modèle de base commun à toutes les entités synchronisées.

Chaque enregistrement porte tout ce qu'il faut pour une synchronisation
hub-and-spoke fiable en environnement intermittent :

- ``id`` : UUID généré localement -> aucune collision de clé entre postes ;
- ``created_at`` / ``updated_at`` : horodatage UTC (USE_TZ=True) ;
- ``is_deleted`` / ``deleted_at`` : suppression logique (tombstone) — on ne
  supprime jamais physiquement, sinon la suppression ne pourrait pas être
  propagée aux autres nœuds ;
- ``origin_node`` : identifiant du nœud qui a produit la dernière écriture,
  utilisé pour départager les conflits (Last-Write-Wins) ;
- ``rev`` : compteur de révisions, incrémenté à chaque sauvegarde.
"""
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class SyncQuerySet(models.QuerySet):
    def actifs(self):
        """Enregistrements non supprimés (usage courant de l'application)."""
        return self.filter(is_deleted=False)


class SyncManager(models.Manager.from_queryset(SyncQuerySet)):
    """Manager par défaut : ne montre que les enregistrements vivants."""

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class SyncModel(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now, editable=False)
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True, editable=False)
    origin_node = models.CharField(max_length=64, editable=False, default="")
    rev = models.PositiveIntegerField(default=0, editable=False)

    # `objects` masque les tombstones ; `all_objects` voit tout (synchro/admin).
    objects = SyncManager()
    all_objects = models.Manager.from_queryset(SyncQuerySet)()

    class Meta:
        abstract = True

    def save(self, *args, sync_apply: bool = False, **kwargs):
        """
        Sauvegarde locale (saisie utilisateur).

        ``sync_apply=True`` est réservé au moteur de synchronisation, qui
        écrit alors les métadonnées telles quelles (sans les régénérer).
        """
        if not sync_apply:
            self.updated_at = timezone.now()
            self.rev = (self.rev or 0) + 1
            if not self.origin_node:
                self.origin_node = settings.NODE_ID
            else:
                self.origin_node = settings.NODE_ID
        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        """Suppression logique : marque le tombstone au lieu d'effacer."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.updated_at = timezone.now()
        self.rev = (self.rev or 0) + 1
        self.origin_node = settings.NODE_ID
        super().save(using=using)

    def hard_delete(self, using=None, keep_parents=False):
        """Suppression physique réelle (maintenance uniquement)."""
        super().delete(using=using, keep_parents=keep_parents)
