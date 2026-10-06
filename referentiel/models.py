import datetime

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone
from django.utils.html import format_html, format_html_join

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


class Marque(SyncModel):
    """Marque de véhicule (HOWO, SHACMAN, FOTON, SHANTUI, …)."""

    nom = models.CharField("Marque", max_length=60, unique=True)

    class Meta:
        verbose_name = "Marque"
        verbose_name_plural = "Marques"
        ordering = ["nom"]

    def __str__(self):
        return self.nom


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
    CAPACITE_CHOICES = [(t, f"{t} tonnes") for t in range(10, 101, 5)]

    immatriculation = models.CharField("Immatriculation", max_length=30)
    marque = models.ForeignKey(
        Marque,
        verbose_name="Marque",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="vehicules",
    )
    # Ancien classement par nombre de roues : conservé en base (données
    # existantes) mais remplacé par la marque dans l'interface.
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
    capacite_tonnes = models.PositiveSmallIntegerField(
        "Capacité", choices=CAPACITE_CHOICES, null=True, blank=True
    )
    numero_chassis = models.CharField("N° de châssis", max_length=50, blank=True)
    actif = models.BooleanField("En service", default=True)

    class Meta:
        verbose_name = "Véhicule"
        verbose_name_plural = "Véhicules"
        ordering = ["immatriculation"]

    def __str__(self):
        return self.immatriculation

    def etat_documents(self):
        """Badges résumant l'état des documents (pour la liste des véhicules)."""
        docs = list(self.documents.all())
        if not docs:
            return format_html('<span class="text-muted small">{}</span>', "Aucun")
        expires = sum(1 for d in docs if d.statut == DocumentVehicule.EXPIRE)
        bientot = sum(1 for d in docs if d.statut == DocumentVehicule.BIENTOT)
        badges = []
        if expires:
            badges.append(("bg-danger", f"{expires} expiré(s)"))
        if bientot:
            badges.append(("bg-warning text-dark", f"{bientot} à renouveler"))
        if not badges:
            badges.append(("bg-success", f"{len(docs)} à jour"))
        return format_html_join(" ", '<span class="badge {}">{}</span>', badges)


def chemin_document(instance, filename):
    """Range les pièces jointes par véhicule : documents_vehicules/<id>/…"""
    return f"documents_vehicules/{instance.vehicule_id}/{instance.type_document}_{filename}"


class DocumentVehicule(SyncModel):
    """Document administratif d'un véhicule (carte grise, assurance, …)."""

    TYPE_CHOICES = [
        ("carte_grise", "Carte grise"),
        ("assurance", "Assurance"),
        ("visite_technique", "Visite technique"),
        ("autorisation_transport", "Autorisation de transport"),
        ("vignette", "Vignette / Taxe"),
        ("autre", "Autre"),
    ]
    EXTENSIONS = ["pdf", "jpg", "jpeg", "png", "webp"]

    # Statuts calculés à partir de la date d'expiration.
    EXPIRE = "expire"
    BIENTOT = "bientot"
    VALIDE = "valide"
    SANS_ECHEANCE = "sans_echeance"

    vehicule = models.ForeignKey(
        Vehicule,
        verbose_name="Véhicule",
        on_delete=models.CASCADE,
        related_name="documents",
    )
    type_document = models.CharField(
        "Type de document", max_length=30, choices=TYPE_CHOICES
    )
    numero = models.CharField("N° du document", max_length=60, blank=True)
    date_emission = models.DateField("Date de délivrance", null=True, blank=True)
    date_expiration = models.DateField(
        "Date d'expiration",
        null=True,
        blank=True,
        help_text="Laisser vide si le document n'expire pas (ex. carte grise).",
    )
    fichier = models.FileField(
        "Fichier (PDF ou photo)",
        upload_to=chemin_document,
        max_length=255,
        blank=True,
        validators=[FileExtensionValidator(EXTENSIONS)],
    )
    observations = models.CharField("Observations", max_length=200, blank=True)

    class Meta:
        verbose_name = "Document véhicule"
        verbose_name_plural = "Documents véhicules"
        ordering = ["date_expiration", "type_document"]

    def __str__(self):
        return f"{self.get_type_document_display()} — {self.vehicule}"

    @staticmethod
    def delai_alerte():
        return datetime.timedelta(days=settings.DOCUMENTS_DELAI_ALERTE_JOURS)

    @property
    def jours_restants(self):
        if not self.date_expiration:
            return None
        return (self.date_expiration - timezone.localdate()).days

    @property
    def statut(self):
        jours = self.jours_restants
        if jours is None:
            return self.SANS_ECHEANCE
        if jours < 0:
            return self.EXPIRE
        if jours <= settings.DOCUMENTS_DELAI_ALERTE_JOURS:
            return self.BIENTOT
        return self.VALIDE

    @property
    def statut_badge(self):
        jours = self.jours_restants
        if self.statut == self.EXPIRE:
            return format_html('<span class="badge bg-danger">Expiré depuis {} j</span>', -jours)
        if self.statut == self.BIENTOT:
            texte = "Expire aujourd'hui" if jours == 0 else f"Expire dans {jours} j"
            return format_html('<span class="badge bg-warning text-dark">{}</span>', texte)
        if self.statut == self.VALIDE:
            return format_html('<span class="badge bg-success">{}</span>', "Valide")
        return format_html('<span class="badge bg-secondary">{}</span>', "Sans échéance")

    @classmethod
    def en_alerte(cls):
        """Documents expirés ou expirant dans le délai d'alerte."""
        limite = timezone.localdate() + cls.delai_alerte()
        return (
            cls.objects.filter(
                date_expiration__isnull=False,
                date_expiration__lte=limite,
                vehicule__is_deleted=False,
            )
            .select_related("vehicule")
            .order_by("date_expiration")
        )


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
