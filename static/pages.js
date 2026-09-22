/* Interacoes somente de leitura para o snapshot do GitHub Pages. */
(function () {
  function normalize(value) {
    return (value || "")
      .toLocaleLowerCase("pt-BR")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "");
  }

  document.querySelectorAll("[data-static-filters]").forEach(function (form) {
    var rows = Array.from(document.querySelectorAll("[data-static-row]"));
    var count = form.parentElement.querySelector("[data-static-count]");
    var empty = form.parentElement.querySelector("[data-static-empty]");

    function applyFilters(event) {
      if (event) event.preventDefault();
      var values = new FormData(form);
      var q = normalize(values.get("q"));
      var situation = values.get("situacao") || "";
      var classification = values.get("classificacao") || "";
      var min = values.get("nota_min") === "" ? null : Number(values.get("nota_min"));
      var max = values.get("nota_max") === "" ? null : Number(values.get("nota_max"));
      var visible = 0;

      rows.forEach(function (row) {
        var scoreText = row.getAttribute("data-static-score") || "";
        var score = scoreText === "" ? null : Number(scoreText);
        var matches = (!q || normalize(row.getAttribute("data-static-search")).includes(q)) &&
          (!situation || row.getAttribute("data-static-situation") === situation) &&
          (!classification || row.getAttribute("data-static-classification") === classification) &&
          (min === null || (score !== null && score >= min)) &&
          (max === null || (score !== null && score <= max));
        row.hidden = !matches;
        var entity = row.getAttribute("data-entity");
        if (entity) {
          var detail = document.querySelector('tr.row-summary-detail[data-detail-for="' + entity + '"]');
          if (detail && !matches) {
            detail.hidden = true;
            detail.setAttribute("aria-hidden", "true");
            var expandBtn = row.querySelector(".row-expand");
            if (expandBtn) expandBtn.setAttribute("aria-expanded", "false");
            row.classList.remove("row-is-expanded");
            row.setAttribute("aria-expanded", "false");
          }
        }
        if (matches) visible += 1;
      });

      if (count) count.textContent = visible + " unidades";
      if (empty) empty.hidden = visible > 0;
    }

    form.addEventListener("submit", applyFilters);
    form.addEventListener("input", applyFilters);
    form.addEventListener("change", applyFilters);
    applyFilters();
  });

  var reportUnit = document.querySelector("[data-static-report-select]");
  if (reportUnit) {
    var pdf = document.getElementById("individual-pdf");
    var xlsx = document.getElementById("individual-xlsx");
    function syncReports() {
      var option = reportUnit.options[reportUnit.selectedIndex];
      if (!option) return;
      if (pdf) pdf.href = option.getAttribute("data-pdf");
      if (xlsx) xlsx.href = option.getAttribute("data-xlsx");
    }
    reportUnit.addEventListener("change", syncReports);
    syncReports();
  }
})();
