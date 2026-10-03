from decimal import Decimal

from django.db import models

from core.models import SyncModel
from referentiel.models import Chauffeur, Vehicule


class PleinCarburant(SyncModel):
    """
    Plein / bon de carburant d'un véhicule.

    Sépare proprement le carburant de l'entretien (mélangés dans le classeur
    d'origine) pour fiabiliser les tableaux de bord de consommation.
    """

    date = models.DateField("Date")
    vehicule = models.ForeignKey(
        Vehicule, verbose_name="Véhicule", on_delete=models.PROTECT,
        related_name="pleins",
    )
    chauffeur = models.ForeignKey(
        Chauffeur, verbose_name="Chauffeur", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="pleins",
    )
    litres = models.DecimalField("Litres", max_digits=10, decimal_places=2, default=0)
    prix_litre = models.DecimalField("Prix / litre", max_digits=10, decimal_places=2, default=0)
    montant = models.DecimalField(
        "Montant", max_digits=14, decimal_places=2, default=0, editable=False
    )
    kilometrage = models.PositiveIntegerField("Kilométrage", null=True, blank=True)
    n_bon = models.CharField("N° du bon", max_length=50, blank=True)
    observation = models.CharField("Observation", max_length=255, blank=True)

    class Meta:
        verbose_name = "Plein de carburant"
        verbose_name_plural = "Pleins de carburant"
        ordering = ["-date"]

    def save(self, *args, **kwargs):
        # Montant recalculé automatiquement (remplace les formules Excel).
        self.montant = (self.litres or Decimal("0")) * (self.prix_litre or Decimal("0"))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.date} — {self.vehicule} — {self.litres} L"
