"""
Importe les données du classeur Excel d'origine dans la base.

Usage :
    python manage.py import_excel "chemin/vers/Flotte.xlsm" --mot-de-passe MDP

- Le référentiel (véhicules, chauffeurs, catégories) est importé en priorité.
- Les écritures (entretien, voyages, Poclain, porte-char, dépenses) sont
  importées au mieux ; les lignes illisibles sont ignorées avec un compte-rendu.
- Ré-exécutable sans doublon pour le référentiel (clé : immatriculation / nom).
"""
import datetime
from decimal import Decimal, InvalidOperation

from django.core.management.base import BaseCommand, CommandError

from carburant.models import PleinCarburant
from depenses.models import AutreDepense
from entretien.models import Entretien
from poclain.models import ActiviteEngin
from portechar.models import TrajetPorteChar
from referentiel.models import CategorieRoues, Chauffeur, Engin, Vehicule
from tools import xlsx_reader
from voyages.models import Voyage

EPOCH = datetime.date(1899, 12, 30)  # base des dates Excel (Windows)


def to_decimal(v):
    if v in (None, ""):
        return Decimal("0")
    try:
        return Decimal(str(v).replace(" ", "").replace(",", "."))
    except (InvalidOperation, ValueError):
        return Decimal("0")


def to_int(v):
    try:
        return int(float(str(v).replace(",", ".")))
    except (ValueError, TypeError):
        return 0


def to_date(v):
    if v in (None, ""):
        return None
    s = str(v).strip()
    # Nombre de série Excel
    try:
        n = float(s)
        if n > 59:
            return EPOCH + datetime.timedelta(days=int(n))
    except ValueError:
        pass
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def g(row, *cles):
    """Récupère la 1re colonne existante parmi plusieurs libellés possibles."""
    for c in cles:
        for k, val in row.items():
            if k.strip().lower() == c.strip().lower():
                return val
    return None


class Command(BaseCommand):
    help = "Importe le classeur Excel d'origine (référentiel + historique)."

    def add_arguments(self, parser):
        parser.add_argument("fichier", help="Chemin du classeur .xlsm/.xlsx")
        parser.add_argument("--mot-de-passe", default=None, help="Mot de passe si le fichier est chiffré")

    def handle(self, *args, **options):
        try:
            z = xlsx_reader.ouvrir(options["fichier"], options["mot_de_passe"])
        except FileNotFoundError:
            raise CommandError("Fichier introuvable.")
        except Exception as exc:
            raise CommandError(f"Ouverture impossible : {exc}")

        tableaux = {t["display"]: t for t in xlsx_reader.lire_tableaux(z)}
        self.stdout.write(f"Tableaux détectés : {', '.join(tableaux) or 'aucun'}")

        self._import_referentiel(tableaux)
        self._import_entretien(tableaux)
        self._import_voyages(tableaux)
        self._import_poclain(tableaux)
        self._import_portechar(tableaux)
        self._import_depenses(tableaux)
        self.stdout.write(self.style.SUCCESS("Import terminé."))

    # --- Référentiel -----------------------------------------------------
    def _vehicule(self, immat):
        immat = (immat or "").strip()
        if not immat:
            return None
        obj = Vehicule.all_objects.filter(immatriculation=immat).first()
        if not obj:
            obj = Vehicule(immatriculation=immat)
            obj.save()
        return obj

    def _chauffeur(self, nom):
        nom = (nom or "").strip()
        if not nom:
            return None
        obj = Chauffeur.all_objects.filter(nom_prenoms=nom).first()
        if not obj:
            obj = Chauffeur(nom_prenoms=nom)
            obj.save()
        return obj

    def _import_referentiel(self, tableaux):
        n_cat = n_ch = n_veh = 0
        # Catégories de roues (Tableau9 : "Nb Roues")
        for t in tableaux.values():
            if any("roue" in c.lower() for c in t["colonnes"]):
                for row in t["lignes"]:
                    lib = str(g(row, "Nb Roues") or "").strip()
                    if lib and not CategorieRoues.all_objects.filter(libelle=lib).exists():
                        CategorieRoues(libelle=lib).save()
                        n_cat += 1
                break
        # Chauffeurs + véhicules (Tableau1 : Prénoms et Noms + Immatriculation)
        for t in tableaux.values():
            cols = [c.lower() for c in t["colonnes"]]
            if any("prénoms" in c or "prenoms" in c for c in cols) and any("immatricul" in c for c in cols):
                for row in t["lignes"]:
                    nom = g(row, "Prénoms et Noms", "Prenoms et Noms")
                    immat = g(row, "Immatriculation")
                    ch = self._chauffeur(nom)
                    if ch:
                        n_ch += 1
                    veh = self._vehicule(immat)
                    if veh:
                        n_veh += 1
                        if ch and not veh.chauffeur_actuel:
                            veh.chauffeur_actuel = ch
                            veh.save()
                break
        self.stdout.write(f"  Référentiel : {n_cat} catégorie(s), {n_ch} chauffeur(s), {n_veh} véhicule(s).")

    # --- Écritures -------------------------------------------------------
    def _import_entretien(self, tableaux):
        n = 0
        for t in tableaux.values():
            cols = [c.lower() for c in t["colonnes"]]
            if any("garage" in c for c in cols) and any("nature" in c for c in cols):
                for row in t["lignes"]:
                    d = to_date(g(row, "Date"))
                    veh = self._vehicule(g(row, "Immatriculation véhicule", "Immatriculation"))
                    if not d or not veh:
                        continue
                    Entretien(
                        date=d, vehicule=veh,
                        chauffeur=self._chauffeur(g(row, "Prénoms et Noms", "Prenoms et Noms")),
                        n_facture=str(g(row, "N° Facture", "N° Facture ") or "")[:50],
                        km_depart=to_int(g(row, "Kilometrage Depart")) or None,
                        km_arrivee=to_int(g(row, "Kilometrage Arrivée")) or None,
                        garage=str(g(row, "GARAGE", "Garage") or "")[:120],
                        nature_operations=str(g(row, "Nature Opérations") or ""),
                        montant_ttc=to_decimal(g(row, "Montant TTC")),
                    ).save()
                    n += 1
                break
        self.stdout.write(f"  Entretien : {n} ligne(s).")

    def _import_voyages(self, tableaux):
        n = 0
        for t in tableaux.values():
            cols = [c.lower() for c in t["colonnes"]]
            if any("nb de voyage" in c for c in cols) and any("bon" in c for c in cols):
                for row in t["lignes"]:
                    d = to_date(g(row, "Date ", "Date"))
                    veh = self._vehicule(g(row, "Immatriculation véhicule", "Immatriculation"))
                    if not d or not veh:
                        continue
                    Voyage(
                        date=d, vehicule=veh,
                        chauffeur=self._chauffeur(g(row, "Prénoms et Noms")),
                        superviseur1=str(g(row, "Superviseur 1") or "")[:120],
                        superviseur2=str(g(row, "Superviseur 2") or "")[:120],
                        n_bon=str(g(row, "N° du Bon", "N° du Bon ") or "")[:50],
                        nb_voyage=to_int(g(row, "Nb de voyage")),
                        pu_voyage=to_decimal(g(row, "PU/Voyage")),
                        km_depart=to_int(g(row, "Kilometrage Depart")) or None,
                        km_arrivee=to_int(g(row, "Kilometrage Arrivée")) or None,
                        nb_heures=to_decimal(g(row, "Nbre d'heure")) or None,
                    ).save()
                    n += 1
                break
        self.stdout.write(f"  Voyages : {n} ligne(s).")

    def _import_poclain(self, tableaux):
        n = 0
        engin = None
        for t in tableaux.values():
            cols = [c.lower() for c in t["colonnes"]]
            if any("chargement" in c for c in cols) and any("carburant" in c for c in cols):
                if engin is None:
                    engin = Engin.all_objects.filter(nom__iexact="Poclain").first() or Engin(nom="Poclain", type_engin="poclain")
                    engin.save()
                for row in t["lignes"]:
                    d = to_date(g(row, "Date"))
                    if not d:
                        continue
                    ActiviteEngin(
                        date=d, engin=engin,
                        nb_chargement=to_int(g(row, "Nb de Chargement")),
                        pu_chargement=to_decimal(g(row, "PU/Chargement")),
                        qte_carburant=to_decimal(g(row, "Qté Carburant")),
                        prix_litre=to_decimal(g(row, "Prix/L")),
                        observation=str(g(row, "Observation") or "")[:255],
                    ).save()
                    n += 1
                break
        self.stdout.write(f"  Poclain : {n} ligne(s).")

    def _import_portechar(self, tableaux):
        n = 0
        for t in tableaux.values():
            cols = [c.lower() for c in t["colonnes"]]
            if any("point depart" in c or "point départ" in c for c in cols):
                for row in t["lignes"]:
                    d = to_date(g(row, "Date"))
                    if not d:
                        continue
                    nom_engin = str(g(row, "Engin") or "").strip()
                    engin = None
                    if nom_engin:
                        engin = Engin.all_objects.filter(nom__iexact=nom_engin).first()
                        if not engin:
                            engin = Engin(nom=nom_engin, type_engin="porte_char")
                            engin.save()
                    TrajetPorteChar(
                        date=d, engin=engin,
                        point_depart=str(g(row, "Point Depart (D)", "Point Départ (D)") or "")[:120],
                        point_arrivee=str(g(row, "Point Arrivé (A)", "Point Arrivée (A)") or "")[:120],
                        km_depart=to_int(g(row, "Kilometrage D")) or None,
                        km_arrivee=to_int(g(row, "Kilometrage A")) or None,
                        montant_paye=to_decimal(g(row, "Montant Payé")),
                    ).save()
                    n += 1
                break
        self.stdout.write(f"  Porte-char : {n} ligne(s).")

    def _import_depenses(self, tableaux):
        n = 0
        for t in tableaux.values():
            cols = [c.lower() for c in t["colonnes"]]
            if any("designation" in c or "désignation" in c for c in cols) and any("prix unitaire" in c for c in cols):
                for row in t["lignes"]:
                    d = to_date(g(row, "Date"))
                    if not d:
                        continue
                    AutreDepense(
                        date=d,
                        designation=str(g(row, "Designation", "Désignation") or "")[:200],
                        prix_unitaire=to_decimal(g(row, "Prix Unitaire")),
                        quantite=to_decimal(g(row, "Quantité")) or Decimal("1"),
                        observation=str(g(row, "Observation") or "")[:255],
                    ).save()
                    n += 1
                break
        self.stdout.write(f"  Autres dépenses : {n} ligne(s).")
