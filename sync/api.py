"""
API de synchronisation (côté SERVEUR / hub central).

Trois points d'entrée, tous authentifiés par jeton (TokenAuthentication) :
- GET  /api/sync/ping/           -> test de connectivité + horodatage serveur
- POST /api/sync/push/           -> le client envoie ses changements locaux
- GET  /api/sync/pull/?since=N   -> le client récupère les changements > N
"""
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .engine import apply_change
from .models import Change

PULL_BATCH = 500


class PingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "ok": True,
            "server_time": timezone.now().isoformat(),
            "node": settings.NODE_ID,
        })


class PushView(APIView):
    """Reçoit une liste de changements et les applique en LWW."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        changes = request.data.get("changes", [])
        applied, skipped = 0, 0
        with transaction.atomic():
            for item in changes:
                model_label = item.get("model")
                payload = item.get("payload")
                if not model_label or not payload:
                    continue
                if apply_change(model_label, payload):
                    applied += 1
                else:
                    skipped += 1
        # Le curseur courant permet au client d'enchaîner un PULL cohérent.
        current_seq = Change.objects.order_by("-seq").values_list("seq", flat=True).first() or 0
        return Response(
            {"applied": applied, "skipped": skipped, "current_seq": current_seq},
            status=status.HTTP_200_OK,
        )


class PullView(APIView):
    """Renvoie les changements dont le seq dépasse ``since``."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            since = int(request.query_params.get("since", 0))
        except (TypeError, ValueError):
            since = 0
        qs = Change.objects.filter(seq__gt=since).order_by("seq")[: PULL_BATCH + 1]
        rows = list(qs)
        has_more = len(rows) > PULL_BATCH
        rows = rows[:PULL_BATCH]
        changes = [
            {
                "seq": c.seq,
                "model": c.model_label,
                "payload": c.payload,
            }
            for c in rows
        ]
        last_seq = rows[-1].seq if rows else since
        return Response({"changes": changes, "last_seq": last_seq, "has_more": has_more})
