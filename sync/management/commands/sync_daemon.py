import time

from django.conf import settings
from django.core.management.base import BaseCommand

from sync.client import SyncError, est_en_ligne, synchroniser


class Command(BaseCommand):
    help = (
        "Synchronisation automatique en boucle : tente une synchro à intervalle "
        "régulier (SYNC_INTERVAL_SECONDS) dès qu'une connexion est disponible."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--intervalle", type=int, default=settings.SYNC_INTERVAL_SECONDS,
            help="Délai entre deux tentatives, en secondes.",
        )

    def handle(self, *args, **options):
        intervalle = options["intervalle"]
        self.stdout.write(
            self.style.SUCCESS(
                f"Démon de synchro démarré (toutes les {intervalle}s). "
                "Ctrl+C pour arrêter."
            )
        )
        while True:
            try:
                if est_en_ligne():
                    res = synchroniser()
                    self.stdout.write(
                        f"[{time.strftime('%H:%M:%S')}] Synchro OK — "
                        f"envoyés: {res.get('envoyes', 0)}, reçus: {res.get('recus', 0)}"
                    )
                else:
                    self.stdout.write(f"[{time.strftime('%H:%M:%S')}] Hors-ligne, on réessaiera.")
            except SyncError as exc:
                self.stderr.write(self.style.WARNING(f"Synchro échouée : {exc}"))
            except KeyboardInterrupt:
                self.stdout.write("\nArrêt du démon.")
                break
            time.sleep(intervalle)
