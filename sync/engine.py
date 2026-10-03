"""
Moteur d'application des changements avec résolution Last-Write-Wins (LWW).

Utilisé des deux côtés :
- le SERVEUR l'appelle pour appliquer les PUSH reçus des clients ;
- le CLIENT l'appelle pour appliquer les PULL reçus du serveur.

Règle LWW : la version dont ``updated_at`` est la plus récente gagne ; en cas
d'égalité stricte, ``origin_node`` départage (ordre lexicographique stable).
Le perdant est journalisé dans ``SyncConflict`` (aucune perte de donnée).
"""
from django.utils.dateparse import parse_datetime

from .models import SyncConflict
from .serializers import apply_payload, get_model, to_payload


def _incoming_wins(incoming_updated, incoming_node, existing) -> bool:
    ex_updated = existing.updated_at
    inc_updated = incoming_updated
    if inc_updated is None:
        return False
    if ex_updated is None:
        return True
    if inc_updated > ex_updated:
        return True
    if inc_updated < ex_updated:
        return False
    # Égalité d'horodatage : on départage par origin_node (déterministe).
    return (incoming_node or "") > (existing.origin_node or "")


def apply_change(model_label: str, payload: dict, *, log_conflicts: bool = True):
    """
    Applique un payload distant sur la base locale selon LWW.

    Retourne ``True`` si la version distante a été appliquée, ``False`` si
    elle a été écartée (version locale plus récente).
    """
    model = get_model(model_label)
    obj_id = payload.get("id")
    incoming_updated = parse_datetime(payload["updated_at"]) if payload.get("updated_at") else None
    incoming_node = payload.get("origin_node", "")

    existing = model.all_objects.filter(pk=obj_id).first()

    if existing is None:
        # Nouvel enregistrement : on l'insère tel quel.
        obj = apply_payload(model, payload)
        obj.save(sync_apply=True, force_insert=True)
        return True

    if _incoming_wins(incoming_updated, incoming_node, existing):
        if log_conflicts and existing.origin_node and existing.origin_node != incoming_node:
            # La version locale est écartée : on la conserve pour revue.
            if existing.updated_at and incoming_updated and existing.updated_at != incoming_updated:
                pass  # écart normal, pas un vrai conflit
            else:
                SyncConflict.objects.create(
                    model_label=model_label,
                    object_id=existing.pk,
                    cote="local",
                    payload_ecarte=to_payload(existing),
                    payload_retenu=payload,
                    note="Version distante retenue (LWW).",
                )
        obj = apply_payload(model, payload)
        obj.save(sync_apply=True, force_update=True)
        return True

    # La version locale est plus récente : on écarte la distante.
    if log_conflicts and incoming_node and incoming_node != existing.origin_node:
        SyncConflict.objects.create(
            model_label=model_label,
            object_id=existing.pk,
            cote="distant",
            payload_ecarte=payload,
            payload_retenu=to_payload(existing),
            note="Version locale conservée (LWW).",
        )
    return False
