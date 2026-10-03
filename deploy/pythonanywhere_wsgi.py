# =====================================================================
#  Exemple de fichier WSGI pour PythonAnywhere
#  À copier-coller dans le fichier WSGI de votre application web
#  (onglet "Web" -> lien "WSGI configuration file"), en remplaçant
#  VOTRECOMPTE et la clé secrète.
# =====================================================================
import os
import sys

# 1) Chemin du projet cloné (adaptez VOTRECOMPTE)
project_home = "/home/VOTRECOMPTE/Gestionnairedeflotte"
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# 2) Variables d'environnement de PRODUCTION
os.environ["NODE_ROLE"] = "server"               # rôle = hub central
os.environ["DJANGO_DEBUG"] = "0"                  # jamais 1 en production
os.environ["DJANGO_SETTINGS_MODULE"] = "fleet.settings.server"

# Clé secrète : générez-la une fois (voir le guide) et collez-la ici.
os.environ["DJANGO_SECRET_KEY"] = "COLLEZ_ICI_UNE_CLE_SECRETE_GENEREE"

# Domaines autorisés et origine de confiance CSRF (adaptez VOTRECOMPTE)
os.environ["DJANGO_ALLOWED_HOSTS"] = "VOTRECOMPTE.pythonanywhere.com"
os.environ["DJANGO_CSRF_TRUSTED"] = "https://VOTRECOMPTE.pythonanywhere.com"

# 3) Démarrage de l'application Django
from fleet.wsgi import application  # noqa: E402
