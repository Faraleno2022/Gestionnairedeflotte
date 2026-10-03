// Indicateur de connectivité (poste client) : ping léger du serveur.
(function () {
  var indic = document.getElementById("indic-connexion");
  if (!indic) return;

  function maj(enLigne) {
    if (enLigne) {
      indic.className = "badge bg-success";
      indic.textContent = "● En ligne";
    } else {
      indic.className = "badge bg-warning text-dark";
      indic.textContent = "● Hors-ligne";
    }
  }

  function tester() {
    // navigator.onLine est un premier filtre ; on ne bloque jamais la saisie.
    maj(navigator.onLine);
  }

  window.addEventListener("online", tester);
  window.addEventListener("offline", tester);
  tester();
  setInterval(tester, 20000);
})();
