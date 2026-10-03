# Gestion de Flotte CAB

Application de gestion de flotte (véhicules, entretien, carburant, voyages,
Poclain, porte-char, dépenses) **fonctionnant hors connexion** sur chaque
poste, avec **synchronisation automatique** vers un serveur central dès que
l'internet revient.

Construite avec **Django 5.2** (Python 3.13). Interface en français.

---

## 1. Architecture

- **Serveur central (hub)** — source de vérité, PostgreSQL (ou SQLite).
  Reçoit et redistribue les changements de tous les postes.
- **Postes nomades (clients)** — chacun une base SQLite locale. Saisie
  possible sans réseau ; envoi/réception au retour de la connexion.

La synchro est en **hub-and-spoke** : clés UUID (pas de collision), suppression
logique (tombstones), journal de changements ordonné, résolution de conflit
**dernier-écrit-gagne** avec traçage (aucune donnée perdue).

Le rôle est choisi par la variable d'environnement `NODE_ROLE`
(`server` ou `client`).

---

## 2. Installation

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

---

## 3. Mise en route du serveur

```bat
set NODE_ROLE=server
python manage.py migrate
python manage.py init_roles --admin-user admin --admin-pass VOTRE_MDP
python manage.py collectstatic --noinput
```

Importer les données du classeur Excel existant :

```bat
python manage.py import_excel "C:\chemin\Flotte CAB Entreprise (2).xlsm" --mot-de-passe VOTRE_MDP_EXCEL
```

Lancer le serveur (réseau local) :

```bat
run_server.bat
```

Pour utiliser **PostgreSQL**, renseignez les variables `POSTGRES_*` dans
`run_server.bat` (sinon SQLite `data_server.sqlite3` est utilisé).

---

## 4. Appairer un poste nomade

Sur le **serveur**, générez le jeton du poste :

```bat
python manage.py appairer_poste poste-01
```

La commande affiche `SYNC_TOKEN=...`. Reportez cette valeur, l'adresse du
serveur et un `NODE_ID` unique dans `run_client.bat`, puis sur le poste :

```bat
run_client.bat
```

Le poste :
- applique ses migrations (base locale) ;
- ouvre l'application sur `http://127.0.0.1:8000` ;
- lance la synchro automatique en tâche de fond (toutes les 5 min) ;
- bouton **🔄 Synchroniser** disponible dans l'interface à tout moment.

---

## 5. Rôles utilisateurs

- **admin** : tout (référentiel, saisie, suppression) ;
- **saisie** : création/modification des écritures **mais pas le référentiel** ;
- **lecture** : consultation seule (les boutons Ajouter/Modifier/Supprimer
  sont masqués et l'accès direct aux formulaires renvoie une erreur 403).

Gérés par groupes Django (créés par `init_roles`), attribuables via
`/admin/`. Les droits sont vérifiés à la fois dans l'affichage (boutons) et
côté serveur (accès aux vues).

---

## 6. Modules

| Module | Contenu |
|--------|---------|
| Référentiel | Véhicules, chauffeurs, catégories de roues, engins |
| Entretien | Charges d'entretien & réparations |
| Carburant | Pleins / bons de carburant (montant calculé) |
| Voyages | Voyages & tonnage par camion |
| Poclain | Chargements + carburant de l'engin |
| Porte-char | Trajets de transport d'engins |
| Autres dépenses | Dépenses diverses |
| Pointage | Grille mensuelle de présence (statut par jour) + totaux automatiques ; gestion des employés |
| Stock | Inventaire (stock calculé + statut OK/Alerte/Rupture), journal des mouvements entrées/sorties, synthèse ; import du classeur Excel |
| Tableau de bord | KPI + graphiques filtrables par année |
| Analyses | Par véhicule : distance, L/100 km, coût au km (carburant + entretien) |
| Rapports | Export **Excel** (multi-feuilles) et **PDF** de synthèse, filtrables par année |

---

## 7. Commandes utiles

```bat
python manage.py sync_now        # une synchro immédiate (client)
python manage.py sync_daemon     # synchro auto en boucle (client)
python manage.py test            # tests automatisés
python manage.py appairer_poste NOM   # jeton d'un poste (serveur)
```

---

## 8. Notes

- Les montants sont **recalculés par l'application** (fin des formules
  Excel cassées `#REF!`).
- Bootstrap et Chart.js sont **inclus en local** (`static/vendor/`) : aucune
  connexion internet n'est requise pour l'affichage.
- Les conflits de synchro sont consultables dans `/admin/sync/syncconflict/`.
