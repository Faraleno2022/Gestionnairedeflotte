from decimal import Decimal

from django.db import models

from core.models import SyncModel
from referentiel.models import Engin


class ActiviteEngin(SyncModel):
    """Activité d'un engin type Poclain : chargements + carburant (Tableau8)."""

    date = models.DateField("Date")
    engin = models.ForeignKey(
        Engin, verbose_name="Engin", on_delete=models.PROTECT,
        related_name="activites",
    )
    nb_chargement = models.PositiveIntegerField("Nombre de chargements", default=0)
    pu_chargement = models.DecimalField("PU / chargement", max_digits=12, decimal_places=2, default=0)
    montant_chargement = models.DecimalField(
        "Montant chargement", max_digits=14, decimal_places=2, default=0, editable=False
    )
    qte_carburant = models.DecimalField("Quantité carburant (L)", max_digits=10, decimal_places=2, default=0)
    prix_litre = models.DecimalField("Prix / litre", max_digits=10, decimal_places=2, default=0)
    montant_carburant = models.DecimalField(
        "Montant carburant", max_digits=14, decimal_places=2, default=0, editable=False
    )
    observation = models.CharField("Observation", max_length=255, blank=True)

    class Meta:
        verbose_name = "Activité d'engin (Poclain)"
        verbose_name_plural = "Activités d'engins (Poclain)"
        ordering = ["-date"]

    def save(self, *args, **kwargs):
        self.montant_chargement = Decimal(self.nb_chargement or 0) * (self.pu_chargement or Decimal("0"))
        self.montant_carburant = (self.qte_carburant or Decimal("0")) * (self.prix_litre or Decimal("0"))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.date} — {self.engin} — {self.nb_chargement} chargement(s)"
