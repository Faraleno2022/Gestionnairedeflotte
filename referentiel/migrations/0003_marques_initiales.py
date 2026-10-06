"""
Pré-remplit les marques courantes de camions et engins.

Les UUID sont dérivés du nom (uuid5) : chaque poste et le serveur créent
exactement les mêmes enregistrements, la synchronisation ne produit donc
aucun doublon.
"""
import uuid

from django.db import migrations
from django.utils import timezone

ESPACE = uuid.UUID("6f1c2a52-7d1e-4f0b-9a49-2b0c5d9e8a10")

MARQUES = [
    "HOWO",
    "SHACMAN",
    "FOTON",
    "SHANTUI",
    "SINOTRUK",
    "SANY",
    "DONGFENG",
    "FAW",
    "MAN",
    "MERCEDES-BENZ",
    "RENAULT",
    "VOLVO",
    "SCANIA",
    "IVECO",
    "TOYOTA",
    "CATERPILLAR",
    "KOMATSU",
]


def creer_marques(apps, schema_editor):
    Marque = apps.get_model("referentiel", "Marque")
    maintenant = timezone.now()
    for nom in MARQUES:
        if Marque.objects.filter(nom=nom).exists():
            continue
        Marque.objects.create(
            id=uuid.uuid5(ESPACE, f"marque:{nom}"),
            nom=nom,
            created_at=maintenant,
            updated_at=maintenant,
            origin_node="migration",
            rev=1,
        )


class Migration(migrations.Migration):

    dependencies = [
        ("referentiel", "0002_marque_capacite_chassis_documents"),
    ]

    operations = [
        migrations.RunPython(creer_marques, migrations.RunPython.noop),
    ]
