from django.core.management.base import BaseCommand

from sync.client import SyncError, synchroniser


class Command(BaseCommand):
    help = "Lance une synchronisation unique (PUSH puis PULL) avec le hub central."

    def handle(self, *args, **options):
        try:
            res = synchroniser()
        except SyncError as exc:
            self.stderr.write(self.style.WARNING(f"Synchro impossible : {exc}"))
            return
        self.stdout.write(
            self.style.SUCCESS(
                f"Synchro OK — envoyés: {res.get('envoyes', 0)}, "
                f"reçus: {res.get('recus', 0)}"
            )
        )
