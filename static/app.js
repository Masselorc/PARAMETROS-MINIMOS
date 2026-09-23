/* Interacoes do detalhe da unidade: PATCH de avaliacao + confirmacoes. */
(function () {
  function toast(msg, isError) {
    var el = document.createElement("div");
    el.className = "notice";
    el.textContent = msg;
    if (isError) el.style.background = "#a42c37";
    document.body.appendChild(el);
    setTimeout(function () { el.remove(); }, 4000);
  }

  function fmt(v) {
    if (v === null || v === undefined) return "—";
    var n = Number(v);
    if (Number.isNaN(n)) return String(v);
    return String(Math.round(n * 10) / 10);
  }

  document.querySelectorAll("[data-confirm]").forEach(function (form) {
    form.addEventListener("submit", function (ev) {
      var msg = form.getAttribute("data-confirm") || "Confirmar?";
      if (!window.confirm(msg)) ev.preventDefault();
    });
  });

  document.querySelectorAll("[data-save]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var card = btn.closest("[data-occurrence]");
      if (!card) return;
      var occurrence = card.getAttribute("data-occurrence");
      var entity = btn.getAttribute("data-entity");
      var sel = card.querySelector("[data-status-select]");
      var ev = card.querySelector("[data-evidence]");
      var msg = card.querySelector("[data-msg]");
      var payload = {
        status: sel ? sel.value : null,
        evidence_text: ev ? ev.value : null,
      };
      btn.disabled = true;
      fetch(
        "/api/unidades/" + encodeURIComponent(entity) +
        "/avaliacoes/" + encodeURIComponent(occurrence),
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        }
      )
        .then(function (resp) {
          if (!resp.ok) throw new Error("HTTP " + resp.status);
          return resp.json();
        })
        .then(function (data) {
          var scoreEl = card.querySelector('[data-score-for]');
          if (scoreEl && data.score !== undefined && data.score !== null) {
            var maxTxt = scoreEl.textContent.split("/")[1] || "";
            scoreEl.textContent = fmt(data.score) + " /" + maxTxt;
          }
          // Sincroniza a nota exibida na sub-aba da pergunta ativa
          var qtabScore = document.querySelector('[data-qtab-score="' + occurrence + '"]');
          if (qtabScore && data.score !== undefined && data.score !== null) {
            var qParts = qtabScore.textContent.split("/");
            var qMax = qParts[1] ? qParts[1].trim() : "";
            qtabScore.textContent = fmt(data.score) + " / " + qMax;
          }
          // total da dimensao: soma client-side a partir dos cartoes visiveis
          var panel = card.closest("[data-dim-panel]");
          if (panel) {
            var dimName = panel.getAttribute("data-dim-panel");
            var badge = document.querySelector('[data-dim-total="' + dimName + '"]');
            if (badge) badge.textContent = fmt(data.dimension_score);
            var floor = document.querySelector('[data-dim-floor="' + dimName + '"]');
            if (floor) {
              if (data.dimension_meets_minimum === true) floor.textContent = "Piso atendido";
              else if (data.dimension_meets_minimum === false) floor.textContent = "Abaixo do mínimo";
            }
          }
          var set = function (id, v) {
            var el = document.getElementById(id);
            if (el) el.textContent = fmt(v);
          };
          set("base-score", data.base_score);
          set("bonus-avail", data.bonus_available);
          set("bonus-applied", data.bonus_applied);
          set("final-score", data.final_score);
          set("final-score-head", data.final_score);
          var finalBar = document.getElementById("final-score-fill");
          if (finalBar && data.final_score !== undefined && data.final_score !== null) {
            var pct = Math.min(100, Math.max(0, Number(data.final_score)));
            finalBar.style.width = pct + "%";
            if (pct >= 70) {
              finalBar.classList.add("gauge-fill-pass");
              finalBar.classList.remove("gauge-fill-fail");
            } else {
              finalBar.classList.add("gauge-fill-fail");
              finalBar.classList.remove("gauge-fill-pass");
            }
          }
          var cls = document.getElementById("classification");
          if (cls && data.classification) cls.textContent = data.classification;
          var clsHead = document.getElementById("classification-head");
          if (clsHead && data.classification) clsHead.textContent = data.classification;
          var meets = document.getElementById("meets-minimum");
          if (meets) {
            if (data.meets_minimum_parameters === true) meets.textContent = "Sim — M1-11 = Sim, nota final ≥ 70 e todas as dimensões essenciais ≥ 50%";
            else if (data.meets_minimum_parameters === false) meets.textContent = "Não — ver pisos dimensionais e nota final abaixo";
          }
          if (msg) msg.textContent = "Alteração salva.";
          toast("Alteração salva.");
        })
        .catch(function () {
          if (msg) msg.textContent = "Não foi possível salvar. Nenhuma alteração foi gravada.";
          toast("Não foi possível salvar. Nenhuma alteração foi gravada.", true);
        })
        .finally(function () { btn.disabled = false; });
    });
  });
})();

/* Interações de filtros avançados e cliente para GitHub Pages e servidor local. */
(function () {
  function normalize(value) {
    return (value || "")
      .toLocaleLowerCase("pt-BR")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .trim();
  }

  function initFilters() {
    var forms = document.querySelectorAll(".filters-bar");
    if (!forms.length) return;

    forms.forEach(function (form) {
      // 1. Inicializa cada Dropdown Multi-Select
      var dropdowns = form.querySelectorAll(".ms-dropdown");

      dropdowns.forEach(function (dd) {
        var trigger = dd.querySelector(".ms-trigger");
        var menu = dd.querySelector(".ms-menu");
        var triggerText = dd.querySelector(".ms-trigger-text");
        var searchInput = dd.querySelector(".ms-search-input");
        var selectAllBtn = dd.querySelector(".ms-select-all");
        var clearAllBtn = dd.querySelector(".ms-clear-all");
        var checkboxes = Array.from(dd.querySelectorAll('input[type="checkbox"]'));
        var filterName = dd.getAttribute("data-filter-name") || "";

        function updateTriggerLabel() {
          if (!triggerText) return;
          var total = checkboxes.length;
          var checked = checkboxes.filter(function (cb) { return cb.checked; });
          var count = checked.length;

          if (count === total) {
            if (filterName === "unidade") triggerText.textContent = "Todas as unidades";
            else if (filterName === "situacao") triggerText.textContent = "Todas as situações";
            else if (filterName === "classificacao") triggerText.textContent = "Todas as classificações";
            else triggerText.textContent = "Todos selecionados";
          } else if (count === 0) {
            triggerText.textContent = "Nenhum selecionado";
          } else if (count === 1) {
            var labelEl = checked[0].closest(".ms-option").querySelector(".ms-option-label");
            triggerText.textContent = labelEl ? labelEl.textContent.trim() : "1 selecionado";
          } else {
            triggerText.textContent = count + " selecionados";
          }
        }

        if (trigger && menu) {
          trigger.addEventListener("click", function (e) {
            e.stopPropagation();
            var isOpen = trigger.getAttribute("aria-expanded") === "true";
            // Fecha outros menus abertos no mesmo formulário
            document.querySelectorAll(".ms-dropdown .ms-trigger[aria-expanded='true']").forEach(function (otherTrig) {
              if (otherTrig !== trigger) {
                otherTrig.setAttribute("aria-expanded", "false");
                var otherMenu = otherTrig.parentElement.querySelector(".ms-menu");
                if (otherMenu) otherMenu.hidden = true;
              }
            });

            trigger.setAttribute("aria-expanded", String(!isOpen));
            menu.hidden = isOpen;
            if (!isOpen && searchInput) {
              setTimeout(function () { searchInput.focus(); }, 50);
            }
          });
        }

        if (searchInput) {
          searchInput.addEventListener("input", function () {
            var q = normalize(searchInput.value);
            dd.querySelectorAll(".ms-option").forEach(function (opt) {
              var text = normalize(opt.textContent);
              opt.style.display = (!q || text.indexOf(q) !== -1) ? "flex" : "none";
            });
          });
        }

        if (selectAllBtn) {
          selectAllBtn.addEventListener("click", function (e) {
            e.preventDefault();
            checkboxes.forEach(function (cb) {
              var opt = cb.closest(".ms-option");
              if (!opt || opt.style.display !== "none") {
                cb.checked = true;
              }
            });
            updateTriggerLabel();
            form.dispatchEvent(new Event("filter-change"));
          });
        }

        if (clearAllBtn) {
          clearAllBtn.addEventListener("click", function (e) {
            e.preventDefault();
            checkboxes.forEach(function (cb) {
              var opt = cb.closest(".ms-option");
              if (!opt || opt.style.display !== "none") {
                cb.checked = false;
              }
            });
            updateTriggerLabel();
            form.dispatchEvent(new Event("filter-change"));
          });
        }

        checkboxes.forEach(function (cb) {
          cb.addEventListener("change", function () {
            updateTriggerLabel();
            form.dispatchEvent(new Event("filter-change"));
          });
        });

        updateTriggerLabel();
      });

      // 2. Inicializa o Dual-Range Slider [ o----------o ]
      var rangeFilter = form.querySelector(".dual-range-filter");
      var rangeMin = form.querySelector(".range-min");
      var rangeMax = form.querySelector(".range-max");
      var rangeProgress = form.querySelector(".range-progress");
      var rangeDisplay = form.querySelector(".range-values");

      function updateRangeSlider() {
        if (!rangeMin || !rangeMax) return;
        var minVal = parseFloat(rangeMin.value);
        var maxVal = parseFloat(rangeMax.value);

        if (minVal > maxVal) {
          var tmp = minVal;
          minVal = maxVal;
          maxVal = tmp;
        }

        if (rangeProgress) {
          rangeProgress.style.left = (minVal) + "%";
          rangeProgress.style.right = (100 - maxVal) + "%";
        }
        if (rangeDisplay) {
          rangeDisplay.textContent = minVal.toFixed(1) + " — " + maxVal.toFixed(1);
        }
      }

      if (rangeMin && rangeMax) {
        rangeMin.addEventListener("input", function () {
          if (parseFloat(rangeMin.value) > parseFloat(rangeMax.value)) {
            rangeMin.value = rangeMax.value;
          }
          updateRangeSlider();
          form.dispatchEvent(new Event("filter-change"));
        });

        rangeMax.addEventListener("input", function () {
          if (parseFloat(rangeMax.value) < parseFloat(rangeMin.value)) {
            rangeMax.value = rangeMin.value;
          }
          updateRangeSlider();
          form.dispatchEvent(new Event("filter-change"));
        });

        updateRangeSlider();
      }

      // 3. Aplicação da Filtragem nas Linhas
      function applyAllFilters() {
        var isReportPage = form.id === "general-report-filters";
        var rows = isReportPage
          ? Array.from(document.querySelectorAll("#general-report-table .general-row"))
          : Array.from(document.querySelectorAll("[data-sort-row]"));

        var countEl = isReportPage
          ? document.getElementById("general-table-count")
          : (form.parentElement.querySelector("[data-static-count]") || document.querySelector("[data-static-count]"));

        var emptyEl = isReportPage
          ? document.getElementById("general-empty-row")
          : (form.parentElement.querySelector("[data-static-empty]") || document.querySelector("[data-static-empty]"));

        // Unidades
        var unitCbs = Array.from(form.querySelectorAll('.ms-dropdown[data-filter-name="unidade"] input[type="checkbox"]'));
        var allUnitsCount = unitCbs.length;
        var selectedUnits = new Set(unitCbs.filter(function (c) { return c.checked; }).map(function (c) { return c.value; }));
        var allUnits = (selectedUnits.size === allUnitsCount);

        // Situação
        var sitCbs = Array.from(form.querySelectorAll('.ms-dropdown[data-filter-name="situacao"] input[type="checkbox"]'));
        var allSitCount = sitCbs.length;
        var selectedSit = new Set(sitCbs.filter(function (c) { return c.checked; }).map(function (c) { return c.value; }));
        var allSit = (selectedSit.size === allSitCount);

        // Classificação
        var clsCbs = Array.from(form.querySelectorAll('.ms-dropdown[data-filter-name="classificacao"] input[type="checkbox"]'));
        var allClsCount = clsCbs.length;
        var selectedCls = new Set(clsCbs.filter(function (c) { return c.checked; }).map(function (c) { return c.value; }));
        var allCls = (selectedCls.size === allClsCount);

        // Faixa de Nota
        var minScore = rangeMin ? parseFloat(rangeMin.value) : 0;
        var maxScore = rangeMax ? parseFloat(rangeMax.value) : 100;
        if (minScore > maxScore) {
          var t = minScore; minScore = maxScore; maxScore = t;
        }

        var visibleCount = 0;

        rows.forEach(function (row) {
          var rowEntity = row.getAttribute("data-entity") || row.getAttribute("data-entity-key") || "";
          var rowUf = row.getAttribute("data-uf") || "";
          var rowSit = row.getAttribute("data-static-situation") || row.getAttribute("data-situacao") || "";
          var rowCls = row.getAttribute("data-static-classification") || row.getAttribute("data-classificacao") || "";
          var scoreRaw = row.getAttribute("data-static-score") || row.getAttribute("data-score");
          var rowScore = (scoreRaw !== null && scoreRaw !== "" && !isNaN(Number(scoreRaw))) ? Number(scoreRaw) : null;

          // 1. Filtro de Unidade
          var matchUnit = allUnits || selectedUnits.has(rowEntity) || selectedUnits.has(rowUf);

          // 2. Filtro de Situação
          var matchSit = allSit || selectedSit.has(rowSit);

          // 3. Filtro de Classificação
          var matchCls = allCls || selectedCls.has(rowCls);

          // 4. Filtro de Nota
          var matchScore = true;
          if (rowScore !== null) {
            matchScore = (rowScore >= minScore - 0.001 && rowScore <= maxScore + 0.001);
          } else {
            // Unidades sem nota (ex.: não instituídas) aparecem se a nota mínima for 0
            matchScore = (minScore <= 0.01);
          }

          var matches = matchUnit && matchSit && matchCls && matchScore;
          row.hidden = !matches;

          // Fecha expansão do card caso a linha seja ocultada
          if (!matches) {
            var entKey = row.getAttribute("data-entity");
            if (entKey) {
              var detail = document.getElementById("detail-" + entKey) || document.querySelector('tr.row-summary-detail[data-detail-for="' + entKey + '"]');
              if (detail) {
                detail.hidden = true;
                detail.setAttribute("aria-hidden", "true");
                var expandBtn = row.querySelector(".row-expand");
                if (expandBtn) expandBtn.setAttribute("aria-expanded", "false");
                row.classList.remove("row-is-expanded");
                row.setAttribute("aria-expanded", "false");
              }
            }
          }

          if (matches) visibleCount++;
        });

        if (countEl) {
          countEl.textContent = isReportPage
            ? ("Exibindo " + visibleCount + " de " + rows.length + " unidades")
            : (visibleCount + " unidades");
        }

        if (emptyEl) {
          emptyEl.hidden = (visibleCount > 0);
        }

        if (isReportPage) {
          var genPdf = document.getElementById("general-pdf");
          var genXlsx = document.getElementById("general-xlsx");
          var qParts = [];
          if (!allSit) {
            selectedSit.forEach(function (s) { qParts.push("situacao=" + encodeURIComponent(s)); });
          }
          if (!allCls) {
            selectedCls.forEach(function (c) { qParts.push("classificacao=" + encodeURIComponent(c)); });
          }
          if (!allUnits) {
            selectedUnits.forEach(function (u) { qParts.push("unidade=" + encodeURIComponent(u)); });
          }
          if (minScore > 0) qParts.push("nota_min=" + minScore);
          if (maxScore < 100) qParts.push("nota_max=" + maxScore);
          var qStr = qParts.length ? ("?" + qParts.join("&")) : "";
          if (genPdf && genPdf.href && genPdf.href.indexOf("/api/relatorios/geral.pdf") !== -1) {
            genPdf.href = "/api/relatorios/geral.pdf" + qStr;
          }
          if (genXlsx && genXlsx.href && genXlsx.href.indexOf("/api/relatorios/geral.xlsx") !== -1) {
            genXlsx.href = "/api/relatorios/geral.xlsx" + qStr;
          }
        }
      }

      form.addEventListener("filter-change", applyAllFilters);
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        applyAllFilters();
      });

      // Aplica imediatamente no carregamento inicial
      applyAllFilters();
    });

    // Fecha menus ao clicar fora
    document.addEventListener("click", function (e) {
      if (!e.target.closest(".ms-dropdown")) {
        document.querySelectorAll(".ms-dropdown .ms-trigger[aria-expanded='true']").forEach(function (trigger) {
          trigger.setAttribute("aria-expanded", "false");
          var menu = trigger.parentElement.querySelector(".ms-menu");
          if (menu) menu.hidden = true;
        });
      }
    });

    // Fecha menus com a tecla Escape
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        document.querySelectorAll(".ms-dropdown .ms-trigger[aria-expanded='true']").forEach(function (trigger) {
          trigger.setAttribute("aria-expanded", "false");
          var menu = trigger.parentElement.querySelector(".ms-menu");
          if (menu) menu.hidden = true;
          trigger.focus();
        });
      }
    });
  }

  // Troca de unidade no relatório individual
  function initReportUnitSelect() {
    var reportUnit = document.querySelector("[data-static-report-select]") || document.getElementById("unit-select");
    if (!reportUnit) return;
    var pdf = document.getElementById("individual-pdf");
    var xlsx = document.getElementById("individual-xlsx");
    var papers = document.querySelectorAll(".unit-report-paper");

    function syncReports() {
      var val = reportUnit.value;
      if (!val) return;

      papers.forEach(function (paper) {
        paper.hidden = (paper.id !== "unit-report-" + val);
      });

      var option = reportUnit.options ? reportUnit.options[reportUnit.selectedIndex] : null;
      if (option && option.getAttribute("data-pdf") && pdf) {
        pdf.href = option.getAttribute("data-pdf");
      }
      if (option && option.getAttribute("data-xlsx") && xlsx) {
        xlsx.href = option.getAttribute("data-xlsx");
      }
    }

    reportUnit.addEventListener("change", syncReports);
    syncReports();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      initFilters();
      initReportUnitSelect();
    });
  } else {
    initFilters();
    initReportUnitSelect();
  }
})();
