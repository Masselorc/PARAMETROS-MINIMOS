/* Fragmentos HTML simples para colagem no editor de documentos do SEI. */
(function () {
  "use strict";

  function escapeHtml(value) {
    return String(value == null ? "" : value).replace(/[&<>"']/g, function (char) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char];
    });
  }

  function clean(value) {
    return String(value == null ? "" : value).replace(/\s+/g, " ").trim();
  }

  function textOf(root, selector) {
    var element = root && root.querySelector(selector);
    return clean(element && element.textContent);
  }

  function score(value) {
    return value === "" || value == null ? "—" : String(value).replace(".", ",");
  }

  function paragraph(value) {
    return "<p style=\"font-family:Arial,sans-serif;font-size:10pt;line-height:1.4;\">" + escapeHtml(value) + "</p>";
  }

  function heading(value, level) {
    var tag = level === 3 ? "h3" : "h2";
    var size = level === 3 ? "11pt" : "13pt";
    return "<" + tag + " style=\"font-family:Arial,sans-serif;font-size:" + size + ";color:#193c46;\">" + escapeHtml(value) + "</" + tag + ">";
  }

  function titleBlock(title, subtitle) {
    return '<table border="1" cellpadding="7" cellspacing="0" width="100%" style="border-collapse:collapse;font-family:Arial,sans-serif;"><tbody><tr><td align="center" bgcolor="#e9eef0" style="border:1px solid #9eacb2;background:#e9eef0;text-align:center;"><strong>' + escapeHtml(title) + '</strong><br>' + escapeHtml(subtitle) + "</td></tr></tbody></table>";
  }

  function table(headers, rows) {
    var html = '<table border="1" cellpadding="5" cellspacing="0" width="100%" style="border-collapse:collapse;font-family:Arial,sans-serif;font-size:9pt;width:100%;"><thead><tr>';
    headers.forEach(function (header) {
      html += '<th scope="col" bgcolor="#e9eef0" style="border:1px solid #9eacb2;background:#e9eef0;text-align:left;vertical-align:top;">' + escapeHtml(header) + "</th>";
    });
    html += "</tr></thead><tbody>";
    rows.forEach(function (row) {
      html += "<tr>";
      row.forEach(function (value) {
        html += '<td style="border:1px solid #9eacb2;vertical-align:top;overflow-wrap:anywhere;">' + escapeHtml(value || "—") + "</td>";
      });
      html += "</tr>";
    });
    return html + "</tbody></table>";
  }

  function filterDescription() {
    var form = document.getElementById("general-report-filters");
    if (!form) return "";
    var parts = [];
    ["unidade", "situacao", "classificacao"].forEach(function (name) {
      var group = form.querySelector('.ms-dropdown[data-filter-name="' + name + '"]');
      if (!group) return;
      var boxes = Array.from(group.querySelectorAll('input[type="checkbox"]'));
      var checked = boxes.filter(function (box) { return box.checked; });
      var labels = checked.map(function (box) {
        var label = box.closest("label");
        return textOf(label, ".ms-option-label") || box.value;
      });
      var nameLabel = { unidade: "Unidades", situacao: "Situações", classificacao: "Classificações" }[name];
      parts.push(nameLabel + ": " + (checked.length === boxes.length ? "todas" : (labels.join(", ") || "nenhuma")));
    });
    var min = form.querySelector(".range-min");
    var max = form.querySelector(".range-max");
    if (min && max) parts.push("Faixa de nota: " + score(min.value) + " a " + score(max.value));
    return parts.join("; ") + ".";
  }

  function generalHtml() {
    var report = document.getElementById("report-geral-doc");
    var source = document.getElementById("general-report-table");
    if (!report || !source) throw new Error("Tabela consolidada indisponível.");
    var visibleRows = Array.from(source.querySelectorAll("tbody tr.general-row")).filter(function (row) {
      return !row.hidden;
    });
    var summaryRows = [];
    var dimensionRows = [];
    visibleRows.forEach(function (row, index) {
      var cells = Array.from(row.cells).map(function (cell) { return clean(cell.textContent); });
      var number = String(index + 1);
      summaryRows.push([number, cells[0], cells[1], cells[8], cells[9], cells[10], cells[11]]);
      dimensionRows.push([number, cells[0], cells[2], cells[3], cells[4], cells[5], cells[6], cells[7]]);
    });
    var html = titleBlock("TABELA CONSOLIDADA DE RESULTADOS", "ONASP — Monitoramento dos Parâmetros Mínimos das Ouvidorias de Serviços Penais");
    html += paragraph("Recorte aplicado: " + filterDescription());
    html += paragraph("Unidades exibidas: " + visibleRows.length + ".");
    if (visibleRows.length) {
      html += heading("Resultados das unidades", 3);
      html += table(["Nº", "UF", "Unidade avaliada", "Nota-base", "Bônus", "Nota final", "Classificação"], summaryRows);
      html += heading("Pontuação por dimensão", 3);
      html += table(["Nº", "UF", "Inst", "Aut", "Imp", "Aces", "Trans", "Integ"], dimensionRows);
      html += paragraph("Legenda: Inst — Institucionalização; Aut — Autonomia; Imp — Imparcialidade; Aces — Acessibilidade; Trans — Transparência; Integ — Integração tecnológica. O número da primeira coluna relaciona as duas tabelas.");
    } else {
      html += paragraph("Nenhuma unidade encontrada com os filtros selecionados.");
    }
    html += paragraph(textOf(report, ".report-note-box"));
    return html;
  }

  function identityHtml(element, subtitle) {
    var data = element.dataset;
    var html = titleBlock("RELATÓRIO DE AVALIAÇÃO — " + data.seiUf + " — " + data.seiUnit, subtitle);
    html += table(["Situação institucional", "Nota-base", "Bônus aplicado", "Nota final", "Classificação"], [[
      data.seiSituation, score(data.seiBase), data.seiBonus === "" ? "—" : "+" + score(data.seiBonus), score(data.seiFinal), data.seiClassification
    ]]);
    return html;
  }

  function individualHtml() {
    var select = document.getElementById("unit-select");
    var paper = select && document.getElementById("unit-report-" + select.value);
    if (!paper) throw new Error("Selecione uma unidade para copiar o relatório.");
    var html = identityHtml(paper, "ONASP — Relatório Individual — IN GABSEC/SENAPPEN/MJSP nº 75/2026 — Metodologia ONASP");
    var dimensionTable = paper.querySelector(".report-dim-table");
    if (dimensionTable) {
      var dimensionHeaders = Array.from(dimensionTable.querySelectorAll("thead th")).map(function (cell) { return clean(cell.textContent); });
      var dimensionRows = Array.from(dimensionTable.querySelectorAll("tbody tr")).map(function (row) {
        return Array.from(row.cells).map(function (cell) { return clean(cell.textContent); });
      });
      html += heading("Pontuação por dimensão e pisos mínimos", 3) + table(dimensionHeaders, dimensionRows);
    }
    paper.querySelectorAll(".report-dim-block").forEach(function (block) {
      html += heading(textOf(block, ".report-dim-title"), 3);
      var questionTable = block.querySelector(".report-q-table");
      if (!questionTable) return;
      var headers = Array.from(questionTable.querySelectorAll("thead th")).map(function (cell) { return clean(cell.textContent); });
      var rows = Array.from(questionTable.querySelectorAll("tbody tr")).map(function (row) {
        return Array.from(row.cells).map(function (cell) { return clean(cell.textContent); });
      });
      html += table(headers, rows);
    });
    html += paragraph(textOf(paper, ".report-note-box"));
    return html;
  }

  function dashboardHtml(button) {
    var detail = button.closest("tr.row-summary-detail");
    if (!detail) throw new Error("Resumo da unidade indisponível.");
    var html = identityHtml(detail, "ONASP — Resumo diagnóstico da Visão Geral");
    var kpis = Array.from(detail.querySelectorAll(".expansion-kpi")).map(function (kpi) {
      return [textOf(kpi, ".kpi-label"), textOf(kpi, ".kpi-val"), textOf(kpi, ".kpi-sub")];
    });
    html += heading("Resultado consolidado", 3) + table(["Indicador", "Resultado", "Referência"], kpis);
    var dimensions = Array.from(detail.querySelectorAll(".dim-card")).map(function (card) {
      return [textOf(card, ".dim-name"), textOf(card, ".dim-score"), textOf(card, ".dim-card-body")];
    });
    html += heading("Dimensões e pisos", 3) + table(["Dimensão", "Pontuação", "Situação"], dimensions);
    var diagnosis = detail.querySelector(".expansion-diag-box");
    if (diagnosis) {
      html += heading("Diagnóstico e motivo da classificação", 3);
      diagnosis.querySelectorAll("p, li").forEach(function (item) {
        html += paragraph(clean(item.textContent).replace(/\s*—\s*Ver perguntas$/, ""));
      });
    }
    return html;
  }

  async function copyHtml(html) {
    if (navigator.clipboard && navigator.clipboard.write && window.ClipboardItem) {
      try {
        await navigator.clipboard.write([new ClipboardItem({
          "text/html": new Blob([html], { type: "text/html" }),
          "text/plain": new Blob([html], { type: "text/plain" })
        })]);
        return;
      } catch (_) { /* tenta as alternativas abaixo */ }
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      try {
        await navigator.clipboard.writeText(html);
        return;
      } catch (_) { /* tenta a seleção de texto */ }
    }
    var field = document.createElement("textarea");
    field.value = html;
    field.setAttribute("readonly", "");
    field.style.cssText = "position:fixed;top:0;left:-9999px;opacity:0;";
    document.body.appendChild(field);
    field.select();
    var copied = document.execCommand("copy");
    field.remove();
    if (!copied) throw new Error("O navegador não permitiu copiar. Verifique a permissão da área de transferência.");
  }

  function notice(message, isError) {
    var element = document.createElement("div");
    element.className = "notice" + (isError ? " failure" : "");
    element.setAttribute("role", "status");
    element.textContent = message;
    document.body.appendChild(element);
    window.setTimeout(function () { element.remove(); }, 5000);
  }

  document.addEventListener("click", async function (event) {
    var button = event.target.closest("[data-sei-copy]");
    if (!button) return;
    try {
      var kind = button.getAttribute("data-sei-copy");
      var html = kind === "general" ? generalHtml() : (kind === "individual" ? individualHtml() : dashboardHtml(button));
      await copyHtml(html);
      notice("HTML copiado. No SEI, abra Código-Fonte e cole o conteúdo.");
    } catch (error) {
      notice(error.message || "Não foi possível copiar o HTML.", true);
    }
  });
})();
