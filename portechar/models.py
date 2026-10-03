from django.db import models

from core.models import SyncModel
from referentiel.models import Engin


class TrajetPorteChar(SyncModel):
    """Trajet de transport d'engin par porte-char (Tableau11)."""

    date = models.DateField("Date")
    engin = models.ForeignKey(
        Engin, verbose_name="Engin transporté", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="trajets_porte_char",
    )
    point_depart = models.CharField("Point de départ", max_length=120)
    point_arrivee = models.CharField("Point d'arrivée", max_length=120)
    km_depart = models.PositiveIntegerField("Kilométrage départ", null=True, blank=True)
    km_arrivee = models.PositiveIntegerField("Kilométrage arrivée", null=True, blank=True)
    montant_paye = models.DecimalField("Montant payé", max_digits=14, decimal_places=2, default=0)
    observation = models.CharField("Observation", max_length=255, blank=True)

    class Meta:
        verbose_name = "Trajet porte-char"
        verbose_name_plural = "Trajets porte-char"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.date} — {self.point_depart} → {self.point_arrivee}"
