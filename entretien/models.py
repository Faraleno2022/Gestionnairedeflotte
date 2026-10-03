from django.db import models

from core.models import SyncModel
from referentiel.models import Chauffeur, Vehicule


class Entretien(SyncModel):
    """Charge d'entretien / réparation d'un véhicule (source : Charges Entretient)."""

    date = models.DateField("Date")
    vehicule = models.ForeignKey(
        Vehicule, verbose_name="Véhicule", on_delete=models.PROTECT,
        related_name="entretiens",
    )
    chauffeur = models.ForeignKey(
        Chauffeur, verbose_name="Chauffeur", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="entretiens",
    )
    n_facture = models.CharField("N° Facture", max_length=50, blank=True)
    km_depart = models.PositiveIntegerField("Kilométrage départ", null=True, blank=True)
    km_arrivee = models.PositiveIntegerField("Kilométrage arrivée", null=True, blank=True)
    garage = models.CharField("Garage", max_length=120, blank=True)
    nature_operations = models.TextField("Nature des opérations", blank=True)
    montant_ttc = models.DecimalField(
        "Montant TTC", max_digits=14, decimal_places=2, default=0
    )
    observation = models.CharField("Observation", max_length=255, blank=True)

    class Meta:
        verbose_name = "Entretien"
        verbose_name_plural = "Entretiens"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.date} — {self.vehicule} — {self.montant_ttc}"
