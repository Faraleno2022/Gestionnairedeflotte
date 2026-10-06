"""Tests du module de pointage de présence."""
import datetime

from django.test import TestCase

from .models import Employe, Pointage
from .views import totaux_employe


class PointageTests(TestCase):
    def setUp(self):
        self.emp = Employe(nom_complet="Test Employé", matricule="T001")
        self.emp.save()

    def test_pk_deterministe(self):
        """Même (employé, date) -> même identifiant (synchro sans doublon)."""
        d = datetime.date(2026, 10, 1)
        self.assertEqual(Pointage.pk_for(self.emp.id, d), Pointage.pk_for(self.emp.id, d))

    def test_totaux(self):
        for jour, statut in [(1, "P"), (2, "A"), (3, "C"), (6, "M"), (7, "P")]:
            d = datetime.date(2026, 10, jour)
            Pointage(id=Pointage.pk_for(self.emp.id, d), employe=self.emp, date=d, statut=statut).save()
        t = totaux_employe(self.emp, 2026, 10)
        # Présence = Présent (2) + Mission (1) = 3
        self.assertEqual(t["nb_presence"], 3)
        self.assertEqual(t["nb_absence"], 1)
        self.assertEqual(t["nb_conge"], 1)
        self.assertEqual(t["nb_mission"], 1)

    def test_enregistrer_upsert_et_suppression(self):
        """L'endpoint AJAX crée, met à jour, puis vide une cellule."""
        from django.contrib.auth.models import Group, User
        Group.objects.get_or_create(name="saisie")
        u = User.objects.create_user("saisie1", password="x")
        u.groups.add(Group.objects.get(name="saisie"))
        self.client.login(username="saisie1", password="x")

        url = "/pointage/enregistrer/"
        # Création
        r = self.client.post(url, {"employe": str(self.emp.id), "date": "2026-10-01", "statut": "P"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["nb_presence"], 1)
        # Mise à jour (même jour -> pas de doublon)
        self.client.post(url, {"employe": str(self.emp.id), "date": "2026-10-01", "statut": "A"})
        self.assertEqual(Pointage.objects.filter(employe=self.emp, date="2026-10-01").count(), 1)
        self.assertEqual(totaux_employe(self.emp, 2026, 10)["nb_absence"], 1)
        # Vidage -> suppression logique
        self.client.post(url, {"employe": str(self.emp.id), "date": "2026-10-01", "statut": ""})
        self.assertEqual(Pointage.objects.filter(employe=self.emp, date="2026-10-01").count(), 0)

    def test_lecture_refuse_enregistrer(self):
        from django.contrib.auth.models import Group, User
        Group.objects.get_or_create(name="lecture")
        u = User.objects.create_user("lect1", password="x")
        u.groups.add(Group.objects.get(name="lecture"))
        self.client.login(username="lect1", password="x")
        r = self.client.post("/pointage/enregistrer/", {
            "employe": str(self.emp.id), "date": "2026-10-01", "statut": "P",
        })
        self.assertEqual(r.status_code, 403)

    def test_retard_et_sanction(self):
        """Retard compte comme présence ; Sanction est comptée à part."""
        from django.contrib.auth.models import User
        self.client.force_login(User.objects.create_superuser("chef", password="x"))
        url = "/pointage/enregistrer/"
        r = self.client.post(url, {"employe": str(self.emp.id), "date": "2026-10-01", "statut": "RT"})
        self.assertEqual(r.json()["nb_retard"], 1)
        self.assertEqual(r.json()["nb_presence"], 1)
        r = self.client.post(url, {"employe": str(self.emp.id), "date": "2026-10-02", "statut": "S"})
        self.assertEqual(r.json()["nb_sanction"], 1)
        self.assertEqual(r.json()["nb_presence"], 1)
        r = self.client.get("/pointage/?mois=2026-10")
        self.assertContains(r, '<option value="RT" title="Retard" selected>')
        self.assertContains(r, "Sanction")

    def test_liste_employes_telephone_permis(self):
        from django.contrib.auth.models import User
        self.emp.telephone = "628 92 01 81"
        self.emp.numero_permis = "GN-123456"
        self.emp.save()
        self.client.force_login(User.objects.create_superuser("chef", password="x"))
        r = self.client.get("/pointage/employes/")
        self.assertContains(r, "<th>Téléphone</th>", html=False)
        self.assertContains(r, "GN-123456")
