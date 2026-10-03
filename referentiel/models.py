from django.db import models

from core.models import SyncModel


class CategorieRoues(SyncModel):
    """Catégorie de véhicule par nombre de roues (6 roues, 10 roues, …)."""

    libelle = models.CharField("Libellé", max_length=50, unique=True)

    class Meta:
        verbose_name = "Catégorie de roues"
        verbose_name_plural = "Catégories de roues"
        ordering = ["libelle"]

    def __str__(self):
        return self.libelle


class Chauffeur(SyncModel):
    nom_prenoms = models.CharField("Prénoms et Noms", max_length=120)
    telephone = models.CharField("Téléphone", max_length=30, blank=True)
    actif = models.BooleanField("Actif", default=True)

    class Meta:
        verbose_name = "Chauffeur"
        verbose_name_plural = "Chauffeurs"
        ordering = ["nom_prenoms"]

    def __str__(self):
        return self.nom_prenoms


class Vehicule(SyncModel):
    immatriculation = models.CharField("Immatriculation", max_length=30)
    categorie_roues = models.ForeignKey(
        CategorieRoues,
        verbose_name="Catégorie de roues",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="vehicules",
    )
    chauffeur_actuel = models.ForeignKey(
        Chauffeur,
        verbose_name="Chauffeur attitré",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="vehicules",
    )
    type_vehicule = models.CharField("Type", max_length=60, blank=True)
    actif = models.BooleanField("En service", default=True)

    class Meta:
        verbose_name = "Véhicule"
        verbose_name_plural = "Véhicules"
        ordering = ["immatriculation"]

    def __str__(self):
        return self.immatriculation


class Engin(SyncModel):
    """Engin spécial : Poclain (pelle/chargeur), porte-char, etc."""

    TYPE_CHOICES = [
        ("poclain", "Poclain / Chargeur"),
        ("porte_char", "Porte-char"),
        ("autre", "Autre"),
    ]
    nom = models.CharField("Nom / Désignation", max_length=80)
    type_engin = models.CharField(
        "Type", max_length=20, choices=TYPE_CHOICES, default="autre"
    )
    actif = models.BooleanField("En service", default=True)

    class Meta:
        verbose_name = "Engin"
        verbose_name_plural = "Engins"
        ordering = ["nom"]

    def __str__(self):
        return self.nom
