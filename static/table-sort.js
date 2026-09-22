/* Ordenacao por cabecalho para tabelas da aplicacao local e do Pages. */
(function () {
  function rawValue(row, column) {
    var cell = row.cells[column];
    if (!cell) return "";
    var explicit = cell.getAttribute("data-sort-value");
    return explicit === null ? cell.textContent.trim() : explicit.trim();
  }

  function numberOrNull(value) {
    if (value === "" || value === "—") return null;
    var number = Number(String(value).replace(",", "."));
    return Number.isFinite(number) ? number : null;
  }

  document.querySelectorAll("table thead th[data-sort-type]").forEach(function (header) {
    var table = header.closest("table");
    var column = header.cellIndex;
    var type = header.getAttribute("data-sort-type");
    var label = header.textContent.trim();
    var button = document.createElement("button");
    button.type = "button";
    button.className = "sort-button";
    button.textContent = "↕";
    button.title = "Ordenar " + label + (type === "number" ? " numericamente" : " alfabeticamente");
    button.setAttribute("aria-label", button.title + "; primeiro clique em ordem crescente");
    header.setAttribute("aria-sort", "none");
    header.appendChild(button);

    button.addEventListener("click", function () {
      var tbody = table.tBodies[0];
      if (!tbody) return;
      var headers = Array.from(table.querySelectorAll("thead th[data-sort-type]"));
      var previous = header.getAttribute("data-sort-direction");
      var direction = previous === "ascending" ? "descending" : "ascending";
      var rows = Array.from(tbody.querySelectorAll("tr[data-sort-row]"));
      var originalOrder = new Map(rows.map(function (row, index) { return [row, index]; }));

      rows.sort(function (a, b) {
        var left = rawValue(a, column);
        var right = rawValue(b, column);
        var result;
        if (type === "number") {
          var leftNumber = numberOrNull(left);
          var rightNumber = numberOrNull(right);
          if (leftNumber === null || rightNumber === null) {
            if (leftNumber === rightNumber) return originalOrder.get(a) - originalOrder.get(b);
            return leftNumber === null ? 1 : -1;
          }
          result = leftNumber - rightNumber;
        } else {
          result = left.localeCompare(right, "pt-BR", { numeric: true, sensitivity: "base" });
        }
        if (result === 0) return originalOrder.get(a) - originalOrder.get(b);
        return direction === "ascending" ? result : -result;
      });

      var emptyRow = tbody.querySelector("[data-static-empty]");
      rows.forEach(function (row) { tbody.insertBefore(row, emptyRow); });
      headers.forEach(function (item) {
        item.removeAttribute("data-sort-direction");
        item.setAttribute("aria-sort", "none");
        var itemButton = item.querySelector(".sort-button");
        if (itemButton) {
          itemButton.textContent = "↕";
          itemButton.setAttribute("aria-label", itemButton.title + "; primeiro clique em ordem crescente");
        }
      });
      header.setAttribute("data-sort-direction", direction);
      header.setAttribute("aria-sort", direction);
      button.textContent = direction === "ascending" ? "↑" : "↓";
      button.setAttribute("aria-label", button.title + (direction === "ascending" ? "; crescente" : "; decrescente"));
    });
  });
})();
