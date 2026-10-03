from decimal import Decimal

from django.db import models

from core.models import SyncModel


class Article(SyncModel):
    """Article d'inventaire (outillage, équipement, consommable…)."""

    code = models.CharField("Code", max_length=40)
    designation = models.CharField("Désignation", max_length=200)
    specification = models.CharField("Spécification", max_length=200, blank=True)
    categorie = models.CharField("Catégorie", max_length=100, blank=True)
    stock_initial = models.DecimalField(
        "Stock initial", max_digits=12, decimal_places=2, default=0
    )
    seuil_mini = models.DecimalField(
        "Seuil minimum", max_digits=12, decimal_places=2, default=0
    )
    observation = models.CharField("Observation", max_length=255, blank=True)

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} — {self.designation}"

    # Statuts calculés
    OK, ALERTE, RUPTURE = "OK", "ALERTE", "RUPTURE"

    @staticmethod
    def statut_pour(stock_actuel, seuil_mini):
        if stock_actuel <= 0:
            return Article.RUPTURE
        if stock_actuel <= (seuil_mini or 0):
            return Article.ALERTE
        return Article.OK

    def stock_actuel(self):
        """Calcul en direct (pour l'admin / le détail). Les listes agrègent en lot."""
        agg = self.mouvements.aggregate(
            e=models.Sum("quantite", filter=models.Q(type=MouvementStock.ENTREE)),
            s=models.Sum("quantite", filter=models.Q(type=MouvementStock.SORTIE)),
        )
        e = agg["e"] or Decimal("0")
        s = agg["s"] or Decimal("0")
        return (self.stock_initial or Decimal("0")) + e - s


class MouvementStock(SyncModel):
    """Entrée ou sortie de stock (journal des mouvements)."""

    ENTREE = "E"
    SORTIE = "S"
    TYPES = [(ENTREE, "Entrée"), (SORTIE, "Sortie")]

    article = models.ForeignKey(
        Article, verbose_name="Article", on_delete=models.CASCADE,
        related_name="mouvements",
    )
    date = models.DateField("Date")
    type = models.CharField("Type", max_length=1, choices=TYPES, default=SORTIE)
    quantite = models.DecimalField("Quantité", max_digits=12, decimal_places=2, default=0)
    motif = models.CharField("Motif / Bénéficiaire", max_length=255, blank=True)
    responsable = models.CharField("Responsable", max_length=120, blank=True)

    class Meta:
        verbose_name = "Mouvement de stock"
        verbose_name_plural = "Mouvements de stock"
        ordering = ["-date"]
        indexes = [models.Index(fields=["date"]), models.Index(fields=["type"])]

    def __str__(self):
        return f"{self.date} — {self.get_type_display()} — {self.article.code} ({self.quantite})"
