"""
Tests de conformité avec le classeur d'origine « Flotte CAB Entreprise ».

Un même jeu de données (décembre 2021) est vérifié contre les formules des
feuilles TB_Gestion, Rapport, Analyse des données du Poclain, Charges
Entretient et Consommation Carburant.
"""
import datetime
from decimal import Decimal as D

from django.contrib.auth.models import User
from django.test import TestCase

from carburant.models import PleinCarburant
from dashboard import services as dash
from depenses.models import AutreDepense
from entretien.models import Entretien
from poclain.models import ActiviteEngin
from portechar.models import TrajetPorteChar
from referentiel.models import CategorieRoues, Chauffeur, Engin, Vehicule
from voyages.models import Voyage

from . import services

DEC = lambda j: datetime.date(2021, 12, j)  # noqa: E731


class ConformiteClasseurTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        r6 = CategorieRoues(libelle="6 Roues"); r6.save()
        r10 = CategorieRoues(libelle="10 Roues"); r10.save()
        ch = Chauffeur(nom_prenoms="Moussa Keira"); ch.save()
        cls.v = Vehicule(immatriculation="AC 5958", chauffeur_actuel=ch); cls.v.save()
        poclain = Engin(nom="Poclain", type_engin="poclain"); poclain.save()

        Entretien(date=DEC(5), vehicule=cls.v, montant_ttc=D("100000")).save()
        PleinCarburant(date=DEC(10), vehicule=cls.v, litres=D("50"), prix_litre=D("12000")).save()
        Voyage(date=DEC(10), vehicule=cls.v, nb_voyage=3, pu_voyage=D("200000")).save()
        Voyage(date=datetime.date(2021, 11, 20), vehicule=cls.v, nb_voyage=1, pu_voyage=D("200000")).save()
        TrajetPorteChar(date=DEC(12), point_depart="A", point_arrivee="B", montant_paye=D("300000")).save()
        ActiviteEngin(date=DEC(10), engin=poclain, categorie_roues=r6, nb_chargement=4,
                      pu_chargement=D("50000"), qte_carburant=D("20"), prix_litre=D("12000")).save()
        ActiviteEngin(date=DEC(11), engin=poclain, categorie_roues=r10, nb_chargement=2,
                      pu_chargement=D("80000")).save()
        AutreDepense(date=DEC(15), designation="Divers", prix_unitaire=D("50000"), quantite=D("1")).save()

    # ---------------------------------------------------------- TB_Gestion
    def test_tb_gestion_mensuel(self):
        t = dash.totaux(2021, 12)
        self.assertEqual(t["litres_carburant"], D("70"))           # 50 véhicule + 20 Poclain
        self.assertEqual(t["depenses_carburant"], D("840000"))     # 600 000 + 240 000
        self.assertEqual(t["depenses_entretien_autres"], D("150000"))
        self.assertEqual(t["depenses_totales"], D("990000"))
        # Porte-char et chargements Poclain sont des RECETTES (pas des dépenses).
        self.assertEqual(t["recettes_camions_portechar"], D("900000"))
        self.assertEqual(t["recettes_poclain"], D("360000"))
        self.assertEqual(t["recettes_totales"], D("1260000"))
        self.assertEqual(t["resultat"], D("270000"))

    def test_tb_gestion_annuel(self):
        t = dash.totaux(2021)
        self.assertEqual(t["recettes_totales"], D("1460000"))      # + voyage de novembre
        self.assertEqual(t["resultat"], D("470000"))

    def test_gestion_mensuel_et_annuel(self):
        g = dash.gestion(2021, 12)
        self.assertEqual(g["resultat_mensuel"], D("270000"))
        self.assertEqual(g["resultat_annuel"], D("470000"))
        self.assertEqual(g["mois_nom"], "décembre")

    # ------------------------------------------------------------- Rapport
    def test_rapport_mensuel(self):
        r = services.rapport_mensuel(2021, 12, DEC(10))
        ligne = next(l for l in r["voyages"] if l["immatriculation"] == "AC 5958")
        self.assertEqual(ligne["chauffeur"], "Moussa Keira")
        self.assertEqual((ligne["mois"], ligne["jour"]), (3, 3))
        carb = {l["immatriculation"]: l for l in r["carburant"]}
        self.assertEqual(carb["AC 5958"]["mois"], D("50"))
        self.assertEqual(carb["Poclain"]["jour"], D("20"))
        self.assertEqual(r["total_litres_mois"], D("70"))

    # ------------------------------------------------------------ Poclain
    def test_analyse_poclain_par_roues(self):
        p = services.analyse_poclain(2021, 12)
        roues = {l["libelle"]: l for l in p["par_roues"]}
        self.assertEqual(roues["6 Roues"]["chargements_mois"], 4)
        self.assertEqual(roues["6 Roues"]["montant_mois"], D("200000"))
        self.assertEqual(roues["10 Roues"]["montant_annee"], D("160000"))
        self.assertEqual(p["carburant"]["litres_mois"], D("20"))
        self.assertEqual(p["carburant"]["montant_mois"], D("240000"))
        self.assertEqual(len(p["journalier"]), 2)

    # ------------------------------------------------------------ Matrices
    def test_charges_entretien_matrice(self):
        m = services.charges_entretien(2021)
        self.assertEqual(m["lignes"][0]["libelle"], "AC 5958")
        self.assertEqual(m["lignes"][0]["valeurs"][11], D("100000"))  # décembre
        self.assertEqual(m["total_general"], D("100000"))

    def test_consommation_carburant_matrice(self):
        m = services.consommation_carburant(2021, "litres")
        lignes = {l["libelle"]: l for l in m["lignes"]}
        self.assertEqual(lignes["AC 5958"]["valeurs"][11], D("50"))
        self.assertEqual(lignes["Poclain (engin)"]["total"], D("20"))
        self.assertEqual(m["total_general"], D("70"))

    # -------------------------------------------------------------- Pages
    def test_pages_accessibles(self):
        User.objects.create_user("u", password="x")
        self.client.login(username="u", password="x")
        for url in [
            "/?annee=2021&mois=12",
            "/rapports/mensuel/?annee=2021&mois=12&jour=2021-12-10",
            "/rapports/charges-entretien/?annee=2021",
            "/rapports/carburant/?annee=2021&unite=montant",
            "/rapports/poclain/?annee=2021&mois=12",
            "/rapports/excel/?annee=2021",
            "/rapports/pdf/?annee=2021",
        ]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_formulaire_prerempli_vehicule(self):
        """Le formulaire d'entretien embarque la correspondance chauffeur -> véhicule."""
        u = User.objects.create_user("adm", password="x", is_superuser=True)
        self.client.force_login(u)
        html = self.client.get("/entretien/ajouter/").content.decode()
        self.assertIn(str(self.v.pk), html)
        self.assertIn("RECHERCHEV", html)
