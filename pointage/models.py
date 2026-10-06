import uuid

from django.db import models

from core.models import SyncModel

# Namespace fixe pour générer des identifiants déterministes de pointage.
# Grâce à lui, un même couple (employé, date) produit le MÊME UUID sur tous
# les postes -> la synchronisation fusionne proprement (pas de doublon).
PTG_NAMESPACE = uuid.UUID("3f2a9c10-6b4e-4d1a-9b7c-0a1b2c3d4e5f")


class Employe(SyncModel):
    """Personnel suivi par le pointage de présence."""

    nom_complet = models.CharField("Nom complet", max_length=150)
    matricule = models.CharField("Matricule", max_length=40)
    fonction = models.CharField("Fonction", max_length=100, blank=True)
    service = models.CharField("Service / Département", max_length=100, blank=True)
    telephone = models.CharField("Téléphone", max_length=30, blank=True)
    numero_permis = models.CharField("N° de permis", max_length=40, blank=True)
    actif = models.BooleanField("Actif", default=True)

    class Meta:
        verbose_name = "Employé"
        verbose_name_plural = "Employés"
        ordering = ["service", "nom_complet"]

    def __str__(self):
        return f"{self.nom_complet} ({self.matricule})"


class Pointage(SyncModel):
    """
    Statut de présence d'un employé pour une journée donnée.

    Un seul pointage par (employé, jour) : l'identifiant est dérivé de ce
    couple (uuid5), ce qui garantit l'unicité et une synchronisation sans
    doublon entre postes.
    """

    PRESENT = "P"
    ABSENT = "A"
    CONGE = "C"
    MISSION = "M"
    REPOS = "R"
    MALADIE = "ML"
    RETARD = "RT"
    SANCTION = "S"

    STATUTS = [
        (PRESENT, "Présent"),
        (ABSENT, "Absent"),
        (CONGE, "Congé"),
        (MISSION, "Mission"),
        (REPOS, "Repos"),
        (MALADIE, "Maladie"),
        (RETARD, "Retard"),
        (SANCTION, "Sanction"),
    ]
    # Statuts comptés comme "présence effective" pour les totaux
    # (un employé en retard est venu travailler).
    STATUTS_PRESENCE = {PRESENT, MISSION, RETARD}

    employe = models.ForeignKey(
        Employe, verbose_name="Employé", on_delete=models.CASCADE,
        related_name="pointages",
    )
    date = models.DateField("Date")
    statut = models.CharField("Statut", max_length=2, choices=STATUTS)

    class Meta:
        verbose_name = "Pointage"
        verbose_name_plural = "Pointages"
        ordering = ["date"]
        indexes = [models.Index(fields=["date"])]

    def __str__(self):
        return f"{self.employe} — {self.date} — {self.statut}"

    @staticmethod
    def pk_for(employe_id, date) -> uuid.UUID:
        """Identifiant déterministe pour un couple (employé, date)."""
        return uuid.uuid5(PTG_NAMESPACE, f"{employe_id}:{date}")
