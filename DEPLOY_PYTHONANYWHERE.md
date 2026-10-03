# Déploiement du hub central sur PythonAnywhere

Guide pas-à-pas pour héberger le **serveur de synchronisation** (rôle `server`)
sur PythonAnywhere. Les postes nomades s'y connecteront ensuite pour synchroniser.

> Durée : ~20 minutes. Plan gratuit suffisant pour démarrer (toujours en ligne, SQLite).

---

## 0. Créer le compte
1. Inscrivez-vous sur https://www.pythonanywhere.com (plan **Beginner / gratuit**).
2. Notez votre nom de compte, ex. `cabentreprise` → votre adresse sera
   `cabentreprise.pythonanywhere.com`.

---

## 1. Cloner le projet
Onglet **Consoles** → ouvrez une console **Bash**, puis :

```bash
git clone https://github.com/Faraleno2022/Gestionnairedeflotte.git
cd Gestionnairedeflotte
```

---

## 2. Créer l'environnement virtuel et installer les dépendances

```bash
python3.11 --version         # vérifiez qu'il existe (sinon python3.10/3.13)
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> `psycopg` (PostgreSQL) peut échouer à s'installer sur le plan gratuit : ce
> n'est pas grave, on utilise SQLite. Si l'installation bloque dessus, retirez
> la ligne `psycopg[binary]` de `requirements.txt` puis relancez `pip install`.

---

## 3. Préparer la base de données (rôle serveur)

```bash
export NODE_ROLE=server
python manage.py migrate
python manage.py init_roles --admin-user admin --admin-pass "UN_MOT_DE_PASSE_FORT"
python manage.py collectstatic --noinput
```

Importer les données du classeur Excel (optionnel — téléversez d'abord le
fichier via l'onglet **Files**) :

```bash
python manage.py import_excel "/home/VOTRECOMPTE/Flotte CAB Entreprise (2).xlsm" --mot-de-passe VOTRE_MDP_EXCEL
```

Générer une **clé secrète** (copiez le résultat pour l'étape 5) :

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 4. Créer l'application web
Onglet **Web** → **Add a new web app** :
1. Choisissez **Manual configuration** (⚠️ pas "Django").
2. Sélectionnez la même version de Python que le venv (ex. **3.11**).

Puis dans la page de l'app web, section **Virtualenv**, indiquez :

```
/home/VOTRECOMPTE/Gestionnairedeflotte/.venv
```

Section **Code**, réglez **Source code** et **Working directory** sur :

```
/home/VOTRECOMPTE/Gestionnairedeflotte
```

---

## 5. Configurer le fichier WSGI
Dans la section **Code**, cliquez sur le lien **WSGI configuration file**.
**Effacez tout** le contenu et remplacez-le par celui de
[`deploy/pythonanywhere_wsgi.py`](deploy/pythonanywhere_wsgi.py) de ce dépôt,
en remplaçant :
- `VOTRECOMPTE` par votre nom de compte,
- la clé secrète par celle générée à l'étape 3.

Enregistrez.

---

## 6. Fichiers statiques
Onglet **Web** → section **Static files**, ajoutez une entrée :

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/VOTRECOMPTE/Gestionnairedeflotte/staticfiles` |

> WhiteNoise sert déjà les statiques, mais cette entrée accélère leur
> distribution. Les deux fonctionnent ensemble.

---

## 7. Démarrer
En haut de l'onglet **Web**, cliquez sur le gros bouton vert **Reload**.

Ouvrez **https://VOTRECOMPTE.pythonanywhere.com/** → connexion avec `admin`
et le mot de passe choisi à l'étape 3. 🎉

---

## 8. Appairer les postes nomades
Dans la console Bash (avec `export NODE_ROLE=server`) :

```bash
python manage.py appairer_poste poste-01
```

Reportez le `SYNC_TOKEN` affiché, avec l'adresse du serveur, dans le
`run_client.bat` de chaque poste :

```bat
set SYNC_SERVER_URL=https://VOTRECOMPTE.pythonanywhere.com
set SYNC_TOKEN=le_jeton_affiché
```

Les postes se synchronisent alors avec ce hub dès qu'ils ont internet.

---

## Mises à jour futures
Quand le code évolue sur GitHub :

```bash
cd ~/Gestionnairedeflotte
source .venv/bin/activate
git pull
export NODE_ROLE=server
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Puis **Reload** dans l'onglet **Web**.

---

## Dépannage
- **Page sans style (CSS manquant)** : relancez `collectstatic`, vérifiez
  l'entrée Static files (étape 6) et faites **Reload**.
- **DisallowedHost** : vérifiez `DJANGO_ALLOWED_HOSTS` dans le WSGI.
- **CSRF verification failed** : vérifiez `DJANGO_CSRF_TRUSTED`
  (`https://VOTRECOMPTE.pythonanywhere.com`).
- **Erreur 502 / rien ne s'affiche** : consultez l'**Error log** (onglet Web).
- **PostgreSQL** : non requis. Pour y passer plus tard (plan payant),
  renseignez les variables `POSTGRES_*` dans le WSGI.
