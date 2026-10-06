"""Tests du référentiel : marques, documents des véhicules et alertes d'expiration."""
import datetime
import shutil
import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from sync.serializers import apply_payload, get_model, to_payload

from .models import DocumentVehicule, Marque, Vehicule

MEDIA_TEST = tempfile.mkdtemp()


def jours(n):
    return timezone.localdate() + datetime.timedelta(days=n)


@override_settings(MEDIA_ROOT=MEDIA_TEST, DOCUMENTS_DELAI_ALERTE_JOURS=30)
class DocumentsTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_TEST, ignore_errors=True)

    def setUp(self):
        self.admin = User.objects.create_superuser("chef", password="x")
        self.client.force_login(self.admin)
        self.v = Vehicule(immatriculation="AC 5958", marque=Marque.objects.get(nom="HOWO"),
                          capacite_tonnes=40, numero_chassis="LZZ5ELND1KW123456")
        self.v.save()

    def _doc(self, expiration, type_document="assurance"):
        d = DocumentVehicule(vehicule=self.v, type_document=type_document, date_expiration=expiration)
        d.save()
        return d

    def test_marques_initiales(self):
        noms = set(Marque.objects.values_list("nom", flat=True))
        self.assertTrue({"HOWO", "SHACMAN", "FOTON", "SHANTUI"} <= noms)

    def test_statuts(self):
        self.assertEqual(self._doc(jours(-1)).statut, DocumentVehicule.EXPIRE)
        self.assertEqual(self._doc(jours(10)).statut, DocumentVehicule.BIENTOT)
        self.assertEqual(self._doc(jours(90)).statut, DocumentVehicule.VALIDE)
        self.assertEqual(self._doc(None, "carte_grise").statut, DocumentVehicule.SANS_ECHEANCE)

    def test_en_alerte_et_badge(self):
        self._doc(jours(-5))
        self._doc(jours(20))
        self._doc(jours(200))
        self.assertEqual(DocumentVehicule.en_alerte().count(), 2)
        r = self.client.get(reverse("dashboard:accueil"))
        self.assertContains(r, "Documents expirés ou à renouveler (2)")
        r = self.client.get(reverse("referentiel:vehicule_liste"))
        self.assertContains(r, "1 expiré(s)")
        self.assertContains(r, "HOWO")
        self.assertContains(r, "40 tonnes")
        self.assertNotContains(r, "<th>Chauffeur</th>")

    def test_televersement_et_consultation(self):
        fichier = SimpleUploadedFile("carte.pdf", b"%PDF-1.4 test", content_type="application/pdf")
        r = self.client.post(reverse("referentiel:document_creer"), {
            "vehicule": self.v.pk, "type_document": "carte_grise", "fichier": fichier,
        })
        self.assertRedirects(r, reverse("referentiel:vehicule_detail", args=[self.v.pk]))
        doc = DocumentVehicule.objects.get()
        r = self.client.get(reverse("referentiel:document_fichier", args=[doc.pk]))
        self.assertEqual(b"".join(r.streaming_content), b"%PDF-1.4 test")
        # Pièce jointe inaccessible sans connexion.
        self.client.logout()
        r = self.client.get(reverse("referentiel:document_fichier", args=[doc.pk]))
        self.assertEqual(r.status_code, 302)

    def test_extension_refusee(self):
        fichier = SimpleUploadedFile("virus.exe", b"MZ", content_type="application/octet-stream")
        r = self.client.post(reverse("referentiel:document_creer"), {
            "vehicule": self.v.pk, "type_document": "autre", "fichier": fichier,
        })
        self.assertEqual(r.status_code, 200)
        self.assertFalse(DocumentVehicule.objects.exists())

    def test_synchro_document(self):
        d = self._doc(jours(10))
        d.fichier.name = "documents_vehicules/x/assurance_police.pdf"
        payload = to_payload(d)
        self.assertEqual(payload["fichier"], "documents_vehicules/x/assurance_police.pdf")
        clone = apply_payload(get_model("referentiel.DocumentVehicule"), payload)
        self.assertEqual(clone.fichier.name, d.fichier.name)
