"""
Tests de la logique de synchronisation (indépendants du réseau).

Couvrent : round-trip de sérialisation, résolution Last-Write-Wins
(insertion, version plus récente qui gagne, version ancienne écartée),
et propagation d'une suppression logique.
"""
import datetime

from django.test import TestCase
from django.utils import timezone

from referentiel.models import Vehicule

from .engine import apply_change
from .models import SyncConflict
from .serializers import apply_payload, get_model, to_payload


class SerializationTests(TestCase):
    def test_round_trip(self):
        v = Vehicule(immatriculation="AC-1234")
        v.save()
        payload = to_payload(v)
        # Les types JSON de base doivent être présents.
        self.assertEqual(payload["immatriculation"], "AC-1234")
        self.assertIsInstance(payload["id"], str)
        # Reconstruction fidèle.
        clone = apply_payload(get_model("referentiel.Vehicule"), payload)
        self.assertEqual(clone.pk, v.pk)
        self.assertEqual(clone.immatriculation, "AC-1234")


class LWWTests(TestCase):
    def _payload_distant(self, immat="XX-000", updated=None, node="autre-poste"):
        v = Vehicule(immatriculation=immat)
        v.save()
        payload = to_payload(v)
        payload["origin_node"] = node
        if updated:
            payload["updated_at"] = updated.isoformat()
        # On retire l'objet local pour simuler un enregistrement purement distant.
        Vehicule.all_objects.filter(pk=v.pk).delete()
        return payload

    def test_insertion_nouveau(self):
        payload = self._payload_distant("NW-1")
        applique = apply_change("referentiel.Vehicule", payload)
        self.assertTrue(applique)
        self.assertTrue(Vehicule.all_objects.filter(immatriculation="NW-1").exists())

    def test_version_distante_plus_recente_gagne(self):
        v = Vehicule(immatriculation="AA-1")
        v.save()
        futur = timezone.now() + datetime.timedelta(hours=1)
        payload = to_payload(v)
        payload["immatriculation"] = "AA-1-MODIF"
        payload["updated_at"] = futur.isoformat()
        payload["origin_node"] = "autre-poste"
        self.assertTrue(apply_change("referentiel.Vehicule", payload))
        self.assertEqual(Vehicule.all_objects.get(pk=v.pk).immatriculation, "AA-1-MODIF")

    def test_version_distante_ancienne_ecartee(self):
        v = Vehicule(immatriculation="BB-1")
        v.save()
        passe = timezone.now() - datetime.timedelta(hours=1)
        payload = to_payload(v)
        payload["immatriculation"] = "BB-1-VIEUX"
        payload["updated_at"] = passe.isoformat()
        payload["origin_node"] = "autre-poste"
        self.assertFalse(apply_change("referentiel.Vehicule", payload))
        # La valeur locale est conservée…
        self.assertEqual(Vehicule.all_objects.get(pk=v.pk).immatriculation, "BB-1")
        # …et le conflit est journalisé (aucune perte).
        self.assertTrue(SyncConflict.objects.filter(object_id=v.pk, cote="distant").exists())

    def test_suppression_logique_se_propage(self):
        v = Vehicule(immatriculation="CC-1")
        v.save()
        futur = timezone.now() + datetime.timedelta(hours=1)
        payload = to_payload(v)
        payload["is_deleted"] = True
        payload["updated_at"] = futur.isoformat()
        payload["origin_node"] = "autre-poste"
        self.assertTrue(apply_change("referentiel.Vehicule", payload))
        # Retiré de la vue courante, mais toujours présent (tombstone).
        self.assertFalse(Vehicule.objects.filter(pk=v.pk).exists())
        self.assertTrue(Vehicule.all_objects.filter(pk=v.pk, is_deleted=True).exists())
