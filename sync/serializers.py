"""
Sérialisation générique des enregistrements synchronisés.

Un payload est un dictionnaire JSON-compatible contenant toutes les colonnes
du modèle (y compris les métadonnées de SyncModel et les clés étrangères
sous forme d'UUID). Aucune dépendance à un serializer par modèle : on lit
directement ``model._meta.fields``.
"""
import datetime
import decimal
import uuid

from django.apps import apps
from django.db.models.fields.files import FieldFile
from django.utils.dateparse import parse_date, parse_datetime


def get_model(model_label):
    return apps.get_model(model_label)


def to_payload(instance) -> dict:
    """Convertit une instance de modèle en dictionnaire JSON-compatible."""
    data = {}
    for field in instance._meta.fields:
        value = getattr(instance, field.attname)
        if value is None:
            data[field.attname] = None
        elif isinstance(value, uuid.UUID):
            data[field.attname] = str(value)
        elif isinstance(value, decimal.Decimal):
            data[field.attname] = str(value)
        elif isinstance(value, (datetime.datetime, datetime.date)):
            data[field.attname] = value.isoformat()
        elif isinstance(value, FieldFile):
            # Seul le chemin voyage : le contenu du fichier reste sur le nœud.
            data[field.attname] = value.name or ""
        else:
            data[field.attname] = value
    return data


def apply_payload(model, payload: dict):
    """
    Construit (sans sauvegarder) une instance à partir d'un payload,
    en reconvertissant les types depuis leur forme JSON.
    """
    fields = {f.attname: f for f in model._meta.fields}
    kwargs = {}
    for key, raw in payload.items():
        field = fields.get(key)
        if field is None:
            continue
        kwargs[key] = _coerce(field, raw)
    return model(**kwargs)


def _coerce(field, raw):
    if raw is None:
        return None
    internal = field.get_internal_type()
    if internal == "UUIDField":
        return uuid.UUID(str(raw))
    if internal == "DecimalField":
        return decimal.Decimal(str(raw))
    if internal == "DateTimeField":
        return parse_datetime(raw) if isinstance(raw, str) else raw
    if internal == "DateField":
        return parse_date(raw) if isinstance(raw, str) else raw
    return raw
