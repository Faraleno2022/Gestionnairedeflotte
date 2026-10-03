from decimal import Decimal

from django.db import models

from core.models import SyncModel
from referentiel.models import Chauffeur, Vehicule


class Voyage(SyncModel):
    """Activité de transport d'un camion (source : BDD Nombre Voyage)."""

    date = models.DateField("Date")
    vehicule = models.ForeignKey(
        Vehicule, verbose_name="Véhicule", on_delete=models.PROTECT,
        related_name="voyages",
    )
    chauffeur = models.ForeignKey(
        Chauffeur, verbose_name="Chauffeur", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="voyages",
    )
    superviseur1 = models.CharField("Superviseur 1", max_length=120, blank=True)
    superviseur2 = models.CharField("Superviseur 2", max_length=120, blank=True)
    n_bon = models.CharField("N° du bon", max_length=50, blank=True)
    nb_voyage = models.PositiveIntegerField("Nombre de voyages", default=0)
    pu_voyage = models.DecimalField("PU / voyage", max_digits=12, decimal_places=2, default=0)
    montant = models.DecimalField(
        "Montant", max_digits=14, decimal_places=2, default=0, editable=False
    )
    km_depart = models.PositiveIntegerField("Kilométrage départ", null=True, blank=True)
    km_arrivee = models.PositiveIntegerField("Kilométrage arrivée", null=True, blank=True)
    nb_heures = models.DecimalField(
        "Nombre d'heures", max_digits=7, decimal_places=2, null=True, blank=True
    )

    class Meta:
        verbose_name = "Voyage"
        verbose_name_plural = "Voyages"
        ordering = ["-date"]

    def save(self, *args, **kwargs):
        self.montant = Decimal(self.nb_voyage or 0) * (self.pu_voyage or Decimal("0"))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.date} — {self.vehicule} — {self.nb_voyage} voyage(s)"
