"""
Client de synchronisation (côté POSTE NOMADE).

S'appuie sur la bibliothèque standard (urllib) pour ne dépendre d'aucun
paquet réseau supplémentaire. Cycle : PING -> PUSH -> PULL.

Utilisable :
- depuis l'interface (bouton « Synchroniser »),
- en ligne de commande : ``python manage.py sync_now``,
- en tâche de fond périodique : ``python manage.py sync_daemon``.
"""
import json
import urllib.error
import urllib.request

from django.apps import apps
from django.conf import settings
from django.utils import timezone

from .engine import apply_change
from .models import NodeState
from .serializers import to_payload


class SyncError(Exception):
    pass


def _request(path, *, method="GET", data=None, timeout=15):
    url = settings.SYNC_SERVER_URL.rstrip("/") + path
    headers = {"Content-Type": "application/json"}
    if settings.SYNC_TOKEN:
        headers["Authorization"] = f"Token {settings.SYNC_TOKEN}"
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise SyncError(f"HTTP {exc.code} sur {path} : {exc.read().decode('utf-8', 'ignore')[:200]}")
    except urllib.error.URLError as exc:
        raise SyncError(f"Réseau indisponible : {exc.reason}")
    except (TimeoutError, OSError) as exc:
        raise SyncError(f"Connexion impossible : {exc}")


def est_en_ligne() -> bool:
    """Teste la connectivité au hub."""
    try:
        _request("/api/sync/ping/", timeout=6)
        return True
    except SyncError:
        return False


def _modeles_synchronises():
    for label in settings.SYNC_MODELS:
        yield label, apps.get_model(label)


def pousser(state: NodeState) -> dict:
    """Envoie au serveur les enregistrements modifiés localement."""
    debut = timezone.now()
    changes = []
    for label, model in _modeles_synchronises():
        qs = model.all_objects.filter(origin_node=settings.NODE_ID)
        if state.last_push_at:
            qs = qs.filter(updated_at__gt=state.last_push_at)
        for obj in qs:
            changes.append({"model": label, "payload": to_payload(obj)})

    if changes:
        _request("/api/sync/push/", method="POST", data={"changes": changes})
    state.last_push_at = debut
    state.save(update_fields=["last_push_at"])
    return {"envoyes": len(changes)}


def tirer(state: NodeState) -> dict:
    """Récupère et applique les changements du serveur."""
    total = 0
    while True:
        res = _request(f"/api/sync/pull/?since={state.last_pulled_seq}")
        rows = res.get("changes", [])
        for row in rows:
            apply_change(row["model"], row["payload"])
            total += 1
        state.last_pulled_seq = res.get("last_seq", state.last_pulled_seq)
        state.save(update_fields=["last_pulled_seq"])
        if not res.get("has_more"):
            break
    return {"recus": total}


def synchroniser() -> dict:
    """Cycle complet PUSH + PULL. Lève SyncError si hors-ligne."""
    if settings.NODE_ROLE != "client":
        raise SyncError("La synchronisation manuelle ne concerne que les postes clients.")
    if not settings.SYNC_TOKEN:
        raise SyncError("Aucun jeton configuré (SYNC_TOKEN). Appairez d'abord le poste au serveur.")

    state = NodeState.get()
    try:
        push = pousser(state)
        pull = tirer(state)
    except SyncError as exc:
        state.last_error = str(exc)
        state.save(update_fields=["last_error"])
        raise

    state.last_sync_ok = timezone.now()
    state.last_error = ""
    state.save(update_fields=["last_sync_ok", "last_error"])
    return {**push, **pull, "date": state.last_sync_ok}
