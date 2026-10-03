"""Tests des droits d'accès par rôle."""
from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from core.permissions import peut_gerer_referentiel, peut_saisir


class PermissionsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        for nom in ["admin", "saisie", "lecture"]:
            Group.objects.get_or_create(name=nom)

    def _user(self, nom, groupe):
        u = User.objects.create_user(nom, password="x")
        u.groups.add(Group.objects.get(name=groupe))
        return u

    def test_roles_helpers(self):
        admin = self._user("a", "admin")
        saisie = self._user("s", "saisie")
        lecture = self._user("l", "lecture")

        self.assertTrue(peut_saisir(admin))
        self.assertTrue(peut_gerer_referentiel(admin))

        self.assertTrue(peut_saisir(saisie))
        self.assertFalse(peut_gerer_referentiel(saisie))

        self.assertFalse(peut_saisir(lecture))
        self.assertFalse(peut_gerer_referentiel(lecture))

    def test_lecture_ne_peut_pas_creer(self):
        self._user("lect", "lecture")
        self.client.login(username="lect", password="x")
        # Accès en création d'une écriture -> interdit (403).
        r = self.client.get(reverse("entretien:creer"))
        self.assertEqual(r.status_code, 403)

    def test_saisie_ne_peut_pas_gerer_referentiel(self):
        self._user("sais", "saisie")
        self.client.login(username="sais", password="x")
        # Peut saisir une écriture…
        self.assertEqual(self.client.get(reverse("entretien:creer")).status_code, 200)
        # …mais pas créer un véhicule (référentiel = admin).
        self.assertEqual(self.client.get(reverse("referentiel:vehicule_creer")).status_code, 403)

    def test_lecture_peut_consulter(self):
        self._user("lo", "lecture")
        self.client.login(username="lo", password="x")
        self.assertEqual(self.client.get(reverse("entretien:liste")).status_code, 200)
        self.assertEqual(self.client.get(reverse("dashboard:accueil")).status_code, 200)
