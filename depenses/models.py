from decimal import Decimal

from django.db import models

from core.models import SyncModel


class AutreDepense(SyncModel):
    """Dépense diverse non rattachée à un véhicule précis (Tableau10)."""

    date = models.DateField("Date")
    designation = models.CharField("Désignation", max_length=200)
    prix_unitaire = models.DecimalField("Prix unitaire", max_digits=12, decimal_places=2, default=0)
    quantite = models.DecimalField("Quantité", max_digits=10, decimal_places=2, default=1)
    montant = models.DecimalField(
        "Montant", max_digits=14, decimal_places=2, default=0, editable=False
    )
    observation = models.CharField("Observation", max_length=255, blank=True)

    class Meta:
        verbose_name = "Autre dépense"
        verbose_name_plural = "Autres dépenses"
        ordering = ["-date"]

    def save(self, *args, **kwargs):
        self.montant = (self.prix_unitaire or Decimal("0")) * (self.quantite or Decimal("0"))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.date} — {self.designation} — {self.montant}"
