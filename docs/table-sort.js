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
    var abbrEl = header.querySelector("abbr");
    var label = header.getAttribute("data-sort-label") || (abbrEl ? abbrEl.getAttribute("title") : "") || header.textContent.trim();
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

      // Fecha todas as expansoes abertas antes de ordenar
      table.querySelectorAll("tr.row-summary-detail").forEach(function (d) {
        d.hidden = true;
        d.setAttribute("aria-hidden", "true");
      });
      table.querySelectorAll(".row-expand").forEach(function (b) {
        b.setAttribute("aria-expanded", "false");
      });
      table.querySelectorAll("tr.row-is-expanded").forEach(function (r) {
        r.classList.remove("row-is-expanded");
        r.setAttribute("aria-expanded", "false");
      });

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
      rows.forEach(function (row) {
        tbody.insertBefore(row, emptyRow);
        var entity = row.getAttribute("data-entity");
        if (entity) {
          var detail = tbody.querySelector('tr.row-summary-detail[data-detail-for="' + entity + '"]');
          if (detail) {
            tbody.insertBefore(detail, emptyRow);
          }
        }
      });
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

  /* Expansao de linha (resumo diagnostico rapido) na dashboard-table */
  function initRowExpansions() {
    document.querySelectorAll(".dashboard-table").forEach(function (table) {
      if (table.getAttribute("data-expansion-initialized") === "true") return;
      table.setAttribute("data-expansion-initialized", "true");

      table.addEventListener("click", function (event) {
        // Ignora cliques dentro da linha de detalhe expandida (permite clicar em links, selecionar texto, etc.)
        if (event.target.closest("tr.row-summary-detail")) {
          return;
        }

        // Ignora cliques em elementos interativos na linha-mãe (ex: botão Detalhar, tooltips, ordenação)
        var interactive = event.target.closest("a, button.btn-detail, .abbr-tooltip, [data-tooltip], input, select, textarea, .sort-button");
        if (interactive && !interactive.classList.contains("row-expand") && !interactive.closest(".row-expand")) {
          return;
        }

        var row = event.target.closest("tr[data-sort-row]");
        if (!row) return;

        var entity = row.getAttribute("data-entity");
        if (!entity) return;

        var detail = table.querySelector('tr.row-summary-detail[data-detail-for="' + entity + '"]');
        if (!detail) return;

        var expandBtn = row.querySelector(".row-expand");
        var isCurrentlyExpanded = !detail.hidden;

        // Regra de UX: apenas uma linha aberta por vez
        table.querySelectorAll("tr.row-summary-detail").forEach(function (d) {
          d.hidden = true;
          d.setAttribute("aria-hidden", "true");
        });
        table.querySelectorAll(".row-expand").forEach(function (b) {
          b.setAttribute("aria-expanded", "false");
        });
        table.querySelectorAll("tr.row-is-expanded").forEach(function (r) {
          r.classList.remove("row-is-expanded");
          r.setAttribute("aria-expanded", "false");
        });

        // Se estava fechada, abre
        if (!isCurrentlyExpanded) {
          detail.hidden = false;
          detail.setAttribute("aria-hidden", "false");
          if (expandBtn) expandBtn.setAttribute("aria-expanded", "true");
          row.classList.add("row-is-expanded");
          row.setAttribute("aria-expanded", "true");
        }
      });

      // Acessibilidade via teclado: Enter e Espaco na linha principal focada
      table.addEventListener("keydown", function (event) {
        if (event.key !== "Enter" && event.key !== " ") return;
        var target = event.target;
        // Se for o proprio botao .row-expand, o browser ja dispara click nativamente
        if (target.classList && (target.classList.contains("row-expand") || target.closest(".row-expand"))) {
          return;
        }
        // Se estiver num link ou outro botao na linha (ex: Detalhar), deixa a acao nativa ocorrer
        if (target.matches("a, button, input, select, textarea")) {
          return;
        }
        var row = target.closest("tr[data-sort-row]");
        if (row) {
          event.preventDefault();
          var btn = row.querySelector(".row-expand");
          if (btn) {
            btn.click();
          } else {
            row.click();
          }
        }
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initRowExpansions);
  } else {
    initRowExpansions();
  }
})();
