// Ouverture/fermeture de la barre latérale sur mobile.
(function () {
  var btn = document.getElementById("btn-menu");
  var backdrop = document.getElementById("sidebar-backdrop");
  function toggle() { document.body.classList.toggle("sidebar-open"); }
  function close() { document.body.classList.remove("sidebar-open"); }
  if (btn) btn.addEventListener("click", toggle);
  if (backdrop) backdrop.addEventListener("click", close);
  // Ferme le menu après un clic sur un lien (petits écrans).
  document.querySelectorAll(".side-link").forEach(function (a) {
    a.addEventListener("click", function () {
      if (window.innerWidth < 992) close();
    });
  });
})();
