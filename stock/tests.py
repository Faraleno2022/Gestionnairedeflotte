"""Tests du module de gestion de stock."""
import datetime
from decimal import Decimal

from django.test import TestCase

from .models import Article, MouvementStock


class StockTests(TestCase):
    def setUp(self):
        self.a = Article(code="REF-100", designation="Test", stock_initial=Decimal("10"),
                         seuil_mini=Decimal("3"))
        self.a.save()

    def _mvt(self, type_, q):
        MouvementStock(article=self.a, date=datetime.date(2026, 6, 1), type=type_,
                       quantite=Decimal(str(q))).save()

    def test_stock_calcule(self):
        self._mvt(MouvementStock.ENTREE, 5)   # +5
        self._mvt(MouvementStock.SORTIE, 4)   # -4
        self.assertEqual(self.a.stock_actuel(), Decimal("11"))  # 10 + 5 - 4

    def test_statut_ok(self):
        self.assertEqual(Article.statut_pour(Decimal("10"), Decimal("3")), Article.OK)

    def test_statut_alerte(self):
        self._mvt(MouvementStock.SORTIE, 8)  # 10 - 8 = 2 <= seuil 3
        stock = self.a.stock_actuel()
        self.assertEqual(Article.statut_pour(stock, self.a.seuil_mini), Article.ALERTE)

    def test_statut_rupture(self):
        self._mvt(MouvementStock.SORTIE, 10)  # 0
        self.assertEqual(
            Article.statut_pour(self.a.stock_actuel(), self.a.seuil_mini), Article.RUPTURE
        )

    def test_inventaire_accessible(self):
        from django.contrib.auth.models import User
        User.objects.create_user("u1", password="x")
        self.client.login(username="u1", password="x")
        self.assertEqual(self.client.get("/stock/").status_code, 200)
        self.assertEqual(self.client.get("/stock/synthese/").status_code, 200)
