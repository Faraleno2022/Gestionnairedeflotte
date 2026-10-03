from django.db import models
from django.utils import timezone


class Change(models.Model):
    """
    Journal de réplication (côté SERVEUR).

    Chaque écriture acceptée par le hub y ajoute une ligne, numérotée par
    ``seq`` (monotone croissant). Les clients tirent (PULL) les changements
    dont ``seq`` dépasse leur dernier curseur connu.
    """

    seq = models.BigAutoField(primary_key=True)
    model_label = models.CharField(max_length=100, db_index=True)
    object_id = models.UUIDField(db_index=True)
    payload = models.JSONField()
    is_deleted = models.BooleanField(default=False)
    node = models.CharField(max_length=64, blank=True)
    ts = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        verbose_name = "Changement (journal)"
        verbose_name_plural = "Changements (journal)"
        ordering = ["seq"]

    def __str__(self):
        return f"#{self.seq} {self.model_label} {self.object_id}"


class NodeState(models.Model):
    """
    État de synchronisation (côté CLIENT). Une seule ligne (singleton).

    - ``last_pulled_seq`` : dernier ``seq`` appliqué depuis le serveur ;
    - ``last_push_at`` : horodatage du dernier PUSH réussi (curseur d'envoi).
    """

    id = models.PositiveSmallIntegerField(primary_key=True, default=1)
    last_pulled_seq = models.BigIntegerField(default=0)
    last_push_at = models.DateTimeField(null=True, blank=True)
    last_sync_ok = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True)

    class Meta:
        verbose_name = "État de synchronisation"
        verbose_name_plural = "État de synchronisation"

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(id=1)
        return obj


class SyncConflict(models.Model):
    """
    Trace d'un conflit résolu en Last-Write-Wins.

    Le « perdant » (version écartée) est conservé ici : aucune donnée n'est
    perdue, un opérateur peut revoir et réappliquer si nécessaire.
    """

    created_at = models.DateTimeField(default=timezone.now)
    model_label = models.CharField(max_length=100)
    object_id = models.UUIDField()
    cote = models.CharField(
        max_length=10,
        choices=[("local", "Local écarté"), ("distant", "Distant écarté")],
    )
    payload_ecarte = models.JSONField()
    payload_retenu = models.JSONField(null=True, blank=True)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Conflit de synchronisation"
        verbose_name_plural = "Conflits de synchronisation"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.model_label} {self.object_id} ({self.cote})"
