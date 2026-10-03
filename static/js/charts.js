// Rendu des graphiques du tableau de bord (Chart.js, vendorisé en local).
(function () {
  var D = window.DASH || {};
  var palette = ["#0d6efd", "#198754", "#212529", "#6c757d", "#ffc107", "#dc3545", "#0dcaf0"];

  function ctx(id) {
    var el = document.getElementById(id);
    return el ? el.getContext("2d") : null;
  }

  // Camembert : répartition des dépenses
  if (D.repartition && ctx("c-repartition")) {
    new Chart(ctx("c-repartition"), {
      type: "doughnut",
      data: {
        labels: D.repartition.labels,
        datasets: [{ data: D.repartition.valeurs, backgroundColor: palette }],
      },
      options: { responsive: true, maintainAspectRatio: false,
        plugins: { legend: { position: "bottom" } } },
    });
  }

  // Barres : charges par véhicule
  if (D.vehicules && ctx("c-vehicules")) {
    new Chart(ctx("c-vehicules"), {
      type: "bar",
      data: {
        labels: D.vehicules.labels,
        datasets: [{ label: "Charges", data: D.vehicules.valeurs, backgroundColor: "#0d6efd" }],
      },
      options: { responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } } },
    });
  }

  // Barres : voyages par véhicule
  if (D.voyages && ctx("c-voyages")) {
    new Chart(ctx("c-voyages"), {
      type: "bar",
      data: {
        labels: D.voyages.labels,
        datasets: [{ label: "Voyages", data: D.voyages.valeurs, backgroundColor: "#198754" }],
      },
      options: { indexAxis: "y", responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } } },
    });
  }

  // Histogramme mensuel : entretien vs carburant
  if (D.mois && ctx("c-mois")) {
    new Chart(ctx("c-mois"), {
      type: "bar",
      data: {
        labels: D.mois.labels,
        datasets: [
          { label: "Entretien", data: D.mois.entretien, backgroundColor: "#0d6efd" },
          { label: "Carburant", data: D.mois.carburant, backgroundColor: "#ffc107" },
        ],
      },
      options: { responsive: true, maintainAspectRatio: false,
        scales: { x: { stacked: false }, y: { beginAtZero: true } } },
    });
  }
})();
