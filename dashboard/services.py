"""
Agrégations pour les tableaux de bord.

Remplace les tableaux croisés dynamiques et formules (cassées) du classeur
Excel par des calculs fiables via l'ORM Django. Toutes les fonctions
acceptent un filtre d'année facultatif.
"""
from decimal import Decimal

from django.db.models import Count, DecimalField, Sum, Value
from django.db.models.functions import Coalesce, ExtractMonth, ExtractYear

from carburant.models import PleinCarburant
from depenses.models import AutreDepense
from entretien.models import Entretien
from poclain.models import ActiviteEngin
from portechar.models import TrajetPorteChar
from referentiel.models import Vehicule
from voyages.models import Voyage

MOIS_FR = [
    "Janv.", "Févr.", "Mars", "Avr.", "Mai", "Juin",
    "Juil.", "Août", "Sept.", "Oct.", "Nov.", "Déc.",
]

_DEC = DecimalField(max_digits=16, decimal_places=2)


def _somme(qs, champ):
    return qs.aggregate(t=Coalesce(Sum(champ), Value(Decimal("0")), output_field=_DEC))["t"]


def annees_disponibles():
    """Liste triée des années présentes dans les données."""
    annees = set()
    for model, champ in [
        (Entretien, "date"), (PleinCarburant, "date"), (Voyage, "date"),
        (ActiviteEngin, "date"), (TrajetPorteChar, "date"), (AutreDepense, "date"),
    ]:
        annees.update(
            model.objects.annotate(a=ExtractYear(champ))
            .values_list("a", flat=True)
            .distinct()
        )
    return sorted(a for a in annees if a)


def _filtrer(qs, annee):
    return qs.filter(date__year=annee) if annee else qs


def totaux(annee=None):
    """Indicateurs clés (KPI) toutes catégories confondues."""
    ent = _filtrer(Entretien.objects, annee)
    carb = _filtrer(PleinCarburant.objects, annee)
    voy = _filtrer(Voyage.objects, annee)
    poc = _filtrer(ActiviteEngin.objects, annee)
    pch = _filtrer(TrajetPorteChar.objects, annee)
    dep = _filtrer(AutreDepense.objects, annee)

    montant_entretien = _somme(ent, "montant_ttc")
    montant_carburant = _somme(carb, "montant")
    litres_carburant = _somme(carb, "litres")
    montant_voyages = _somme(voy, "montant")
    nb_voyages = voy.aggregate(t=Coalesce(Sum("nb_voyage"), 0))["t"]
    montant_poclain = _somme(poc, "montant_chargement") + _somme(poc, "montant_carburant")
    montant_portechar = _somme(pch, "montant_paye")
    montant_depenses = _somme(dep, "montant")

    depenses_totales = (
        montant_entretien + montant_carburant + montant_poclain
        + montant_portechar + montant_depenses
    )

    return {
        "montant_entretien": montant_entretien,
        "montant_carburant": montant_carburant,
        "litres_carburant": litres_carburant,
        "montant_voyages": montant_voyages,
        "nb_voyages": nb_voyages,
        "montant_poclain": montant_poclain,
        "montant_portechar": montant_portechar,
        "montant_depenses": montant_depenses,
        "depenses_totales": depenses_totales,
        "recettes_voyages": montant_voyages,
        "nb_vehicules": Vehicule.objects.count(),
    }


def repartition_depenses(annee=None):
    """Montant par catégorie de dépense (pour un camembert)."""
    t = totaux(annee)
    return {
        "labels": ["Entretien", "Carburant", "Poclain", "Porte-char", "Autres"],
        "valeurs": [
            float(t["montant_entretien"]),
            float(t["montant_carburant"]),
            float(t["montant_poclain"]),
            float(t["montant_portechar"]),
            float(t["montant_depenses"]),
        ],
    }


def depenses_par_mois(annee):
    """Entretien vs carburant par mois pour une année (histogramme)."""
    def par_mois(qs, champ):
        data = {i: Decimal("0") for i in range(1, 13)}
        rows = (
            qs.filter(date__year=annee)
            .annotate(m=ExtractMonth("date"))
            .values("m")
            .annotate(t=Coalesce(Sum(champ), Value(Decimal("0")), output_field=_DEC))
        )
        for r in rows:
            data[r["m"]] = r["t"]
        return [float(data[i]) for i in range(1, 13)]

    return {
        "labels": MOIS_FR,
        "entretien": par_mois(Entretien.objects, "montant_ttc"),
        "carburant": par_mois(PleinCarburant.objects, "montant"),
    }


def charges_par_vehicule(annee=None):
    """Charges d'entretien + carburant par véhicule (barres)."""
    resultats = {}
    ent = _filtrer(Entretien.objects, annee).values("vehicule__immatriculation").annotate(
        t=Coalesce(Sum("montant_ttc"), Value(Decimal("0")), output_field=_DEC)
    )
    carb = _filtrer(PleinCarburant.objects, annee).values("vehicule__immatriculation").annotate(
        t=Coalesce(Sum("montant"), Value(Decimal("0")), output_field=_DEC)
    )
    for r in ent:
        resultats.setdefault(r["vehicule__immatriculation"] or "—", Decimal("0"))
        resultats[r["vehicule__immatriculation"] or "—"] += r["t"]
    for r in carb:
        resultats.setdefault(r["vehicule__immatriculation"] or "—", Decimal("0"))
        resultats[r["vehicule__immatriculation"] or "—"] += r["t"]
    items = sorted(resultats.items(), key=lambda kv: kv[1], reverse=True)
    return {
        "labels": [k for k, _ in items],
        "valeurs": [float(v) for _, v in items],
    }


def _distances_par_vehicule(annee):
    """
    Estime la distance parcourue par véhicule (km max - km min observés),
    à partir des kilométrages saisis dans pleins, entretiens et voyages.
    """
    bornes = {}  # immat -> [min, max]

    def integrer(immat, valeur):
        if immat is None or valeur in (None, 0):
            return
        b = bornes.setdefault(immat, [valeur, valeur])
        b[0] = min(b[0], valeur)
        b[1] = max(b[1], valeur)

    sources = [
        (_filtrer(PleinCarburant.objects, annee), ["kilometrage"]),
        (_filtrer(Entretien.objects, annee), ["km_depart", "km_arrivee"]),
        (_filtrer(Voyage.objects, annee), ["km_depart", "km_arrivee"]),
    ]
    for qs, champs in sources:
        vals = qs.values_list("vehicule__immatriculation", *champs)
        for row in vals:
            immat = row[0]
            for v in row[1:]:
                integrer(immat, v)

    return {immat: (b[1] - b[0]) for immat, b in bornes.items() if b[1] > b[0]}


def analyse_vehicules(annee=None):
    """
    Tableau d'analyse par véhicule : distance, litres, L/100km, coûts au km.

    Renvoie une liste de dictionnaires triée par coût total au km décroissant.
    """
    distances = _distances_par_vehicule(annee)

    litres = {
        r["vehicule__immatriculation"]: r["l"]
        for r in _filtrer(PleinCarburant.objects, annee)
        .values("vehicule__immatriculation")
        .annotate(l=Coalesce(Sum("litres"), Value(Decimal("0")), output_field=_DEC))
    }
    cout_carb = {
        r["vehicule__immatriculation"]: r["m"]
        for r in _filtrer(PleinCarburant.objects, annee)
        .values("vehicule__immatriculation")
        .annotate(m=Coalesce(Sum("montant"), Value(Decimal("0")), output_field=_DEC))
    }
    cout_ent = {
        r["vehicule__immatriculation"]: r["m"]
        for r in _filtrer(Entretien.objects, annee)
        .values("vehicule__immatriculation")
        .annotate(m=Coalesce(Sum("montant_ttc"), Value(Decimal("0")), output_field=_DEC))
    }
    nb_voy = {
        r["vehicule__immatriculation"]: r["n"]
        for r in _filtrer(Voyage.objects, annee)
        .values("vehicule__immatriculation")
        .annotate(n=Coalesce(Sum("nb_voyage"), 0))
    }

    immats = set(litres) | set(cout_carb) | set(cout_ent) | set(nb_voy) | set(distances)
    lignes = []
    for immat in immats:
        if not immat:
            continue
        dist = distances.get(immat)
        l = float(litres.get(immat, 0) or 0)
        cc = float(cout_carb.get(immat, 0) or 0)
        ce = float(cout_ent.get(immat, 0) or 0)
        total = cc + ce
        lignes.append({
            "vehicule": immat,
            "distance": dist,
            "litres": l,
            "montant_carburant": cc,
            "montant_entretien": ce,
            "montant_total": total,
            "nb_voyages": nb_voy.get(immat, 0),
            "l_100km": round(l / dist * 100, 2) if dist else None,
            "cout_carburant_km": round(cc / dist, 2) if dist else None,
            "cout_entretien_km": round(ce / dist, 2) if dist else None,
            "cout_total_km": round(total / dist, 2) if dist else None,
        })
    lignes.sort(key=lambda x: (x["cout_total_km"] or 0, x["montant_total"]), reverse=True)
    return lignes


def voyages_par_vehicule(annee=None):
    """Nombre de voyages par véhicule (barres)."""
    rows = (
        _filtrer(Voyage.objects, annee)
        .values("vehicule__immatriculation")
        .annotate(nb=Coalesce(Sum("nb_voyage"), 0))
        .order_by("-nb")
    )
    return {
        "labels": [r["vehicule__immatriculation"] or "—" for r in rows],
        "valeurs": [r["nb"] for r in rows],
    }
