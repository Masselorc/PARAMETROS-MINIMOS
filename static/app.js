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

  function getStatusType(val) {
    if (!val) return "neutral";
    var clean = String(val).trim().normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
    if (clean === "atende" || clean === "sim") return "good";
    if (clean === "parcial" || clean === "atende parcialmente") return "warn";
    if (clean === "nao" || clean === "nao atende" || clean.indexOf("nao") !== -1) return "bad";
    return "neutral";
  }

  function updateStatusSelectColor(sel) {
    if (!sel) return;
    var val = sel.value;
    var type = getStatusType(val);
    sel.setAttribute("data-status-val", val);
    sel.setAttribute("data-status-type", type);
    sel.classList.remove("status-good", "status-warn", "status-bad", "status-neutral");
    sel.classList.add("status-" + type);
  }
  window.updateStatusSelectColor = updateStatusSelectColor;

  function setCriterionState(id, passed) {
    var item = document.getElementById(id);
    if (!item) return;
    item.classList.remove("crit-pass", "crit-fail");
    item.classList.add(passed ? "crit-pass" : "crit-fail");
    var icon = item.querySelector(".crit-icon");
    if (icon) icon.textContent = passed ? "✓" : "✗";
  }

  function updateResultBadge(passed) {
    var wrap = document.getElementById("result-badge-status");
    if (!wrap) return;
    var pill = wrap.querySelector(".status-pill-lg");
    if (!pill) {
      pill = document.createElement("span");
      wrap.appendChild(pill);
    }
    pill.className = "status-pill-lg " + (passed ? "status-pass" : "status-fail");

    var svg = pill.querySelector("svg");
    if (!svg) svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("class", "status-icon-svg");
    svg.setAttribute("viewBox", "0 0 20 20");
    svg.setAttribute("fill", "currentColor");
    svg.setAttribute("width", "18");
    svg.setAttribute("height", "18");
    var path = svg.querySelector("path");
    if (!path) path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("fill-rule", "evenodd");
    path.setAttribute("clip-rule", "evenodd");
    path.setAttribute("d", passed
      ? "M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
      : "M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z");
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    svg.appendChild(path);
    var label = document.createTextNode(passed
      ? " Segue os Parâmetros Mínimos"
      : " Abaixo dos Parâmetros Mínimos");
    pill.replaceChildren(svg, label);
  }

  function updateResultSummary(data) {
    var situation = data.situacao;
    var situationPassed = situation === "Instituída";
    var badge = document.getElementById("head-badge-situacao");
    if (badge && situation) {
      badge.textContent = situation;
      badge.classList.remove("badge-good", "badge-bad", "badge-warn");
      badge.classList.add(situationPassed ? "badge-good" : (situation === "Não instituída" ? "badge-bad" : "badge-warn"));
    }

    var classification = data.classification;
    var classificationText = document.getElementById("classification");
    if (classificationText && classification) classificationText.textContent = classification;
    var classificationHead = document.getElementById("classification-head");
    if (classificationHead && classification) classificationHead.textContent = classification;
    var classificationCard = document.getElementById("result-classification-card");
    if (classificationCard && classification) {
      var cardClass = "class-bad";
      if (classification === "Instituída — seguindo os parâmetros mínimos") cardClass = "class-good";
      else if (classification === "Instituída — abaixo do mínimo em dimensão essencial") cardClass = "class-warn";
      else if (classification === "Instituída — aderência global insuficiente") cardClass = "class-info";
      classificationCard.classList.remove("class-good", "class-warn", "class-info", "class-bad");
      classificationCard.classList.add(cardClass);
    }

    var globalPassed = Number(data.final_score) >= 70;
    var dimensionsBelow = Array.isArray(data.dimensions_below_minimum) ? data.dimensions_below_minimum : null;
    var dimensionsPassed = dimensionsBelow ? dimensionsBelow.length === 0 : false;
    setCriterionState("criteria-item-situacao", situationPassed);
    setCriterionState("criteria-item-piso", globalPassed);
    if (dimensionsBelow) setCriterionState("criteria-item-dimensoes", dimensionsPassed);

    var situationText = document.getElementById("criteria-text-situacao");
    if (situationText && situation) {
      situationText.textContent = situationPassed
        ? "Ato normativo de criação comprovado (Situação: Instituída)"
        : "Situação: " + situation + " (sem ato formal específico)";
    }
    var globalText = document.getElementById("criteria-text-piso");
    var globalValue = globalText && globalText.querySelector("strong");
    if (globalValue && data.final_score !== undefined) globalValue.textContent = fmt(data.final_score);
    var dimensionsText = document.getElementById("criteria-text-dimensoes");
    if (dimensionsText && dimensionsBelow) {
      dimensionsText.textContent = dimensionsPassed
        ? "Todas as 6 dimensões essenciais atingiram o piso mínimo"
        : "Abaixo do piso em " + dimensionsBelow.length + " dimensão(ões) essencial(is)";
    }

    updateResultBadge(data.meets_minimum_parameters === true);
    var meets = document.getElementById("meets-minimum");
    if (meets) {
      if (data.meets_minimum_parameters === true) {
        meets.textContent = "Sim — M1-11 = Sim, nota final ≥ 70 e todas as dimensões essenciais ≥ 50%";
      } else {
        var reasons = [];
        if (situation && !situationPassed) reasons.push("M1-11");
        if (data.final_score !== null && data.final_score !== undefined && !globalPassed) reasons.push("nota final");
        if (dimensionsBelow && dimensionsBelow.length) reasons.push("pisos dimensionais");
        meets.textContent = "Não — verifique " + (reasons.length ? reasons.join(", ") : "os critérios obrigatórios") + ".";
      }
    }
  }

  document.querySelectorAll("[data-status-select]").forEach(function (sel) {
    sel.addEventListener("change", function () {
      updateStatusSelectColor(sel);
    });
    sel.addEventListener("input", function () {
      updateStatusSelectColor(sel);
    });
    updateStatusSelectColor(sel);
  });

  document.addEventListener("change", function (e) {
    var sel = e.target && e.target.closest ? e.target.closest("[data-status-select]") : null;
    if (sel) updateStatusSelectColor(sel);
  });
  document.addEventListener("input", function (e) {
    var sel = e.target && e.target.closest ? e.target.closest("[data-status-select]") : null;
    if (sel) updateStatusSelectColor(sel);
  });

  document.querySelectorAll("[data-save]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var card = btn.closest(".qcard") || btn.closest("[data-q-panel]");
      var occurrence = btn.getAttribute("data-occurrence") || (card ? card.getAttribute("data-occurrence") : "");
      var entity = btn.getAttribute("data-entity");
      /* Busca o select e textarea: primeiro dentro do card, depois por ID como fallback */
      var sel = null;
      var ev = null;
      if (card) {
        sel = card.querySelector("[data-status-select]");
        ev = card.querySelector("[data-evidence]");
      }
      if (!sel && occurrence) sel = document.getElementById("status-" + occurrence);
      if (!ev && occurrence) ev = document.getElementById("evidence-" + occurrence);
      /* Fallback extra: busca pela classe do edit-box mais próxima ao botão */
      if (!sel) {
        var editBox = btn.closest(".eval-edit-box") || btn.closest(".eval-ctrl-bar");
        if (editBox) sel = editBox.querySelector("[data-status-select]");
      }
      var msg = card ? card.querySelector("[data-msg]") : (btn.parentElement ? btn.parentElement.querySelector("[data-msg]") : null);
      if (!sel) {
        console.error("[Salvar] select de status não encontrado. occurrence=" + occurrence + ", entity=" + entity);
        toast("Erro interno: campo de status não encontrado.", true);
        return;
      }
      var payload = {
        status: sel ? sel.value : null,
        evidence_text: ev ? ev.value : null,
      };
      console.log("[Salvar] Enviando PATCH:", entity, occurrence, payload);
      btn.disabled = true;
      if (msg) { msg.textContent = "Salvando…"; msg.style.color = ""; }
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
          if (!resp.ok) {
            return resp.json().catch(function () { return {}; }).then(function (errData) {
              var detail = (errData && errData.detail) ? errData.detail : ("Erro HTTP " + resp.status);
              var httpErr = new Error(detail);
              httpErr.httpStatus = resp.status;
              throw httpErr;
            });
          }
          return resp.json();
        })
        .then(function (data) {
          console.log("[Salvar] Resposta OK:", data);
          var scoreEl = card ? card.querySelector('[data-score-for]') : null;
          if (scoreEl && data.score !== undefined && data.score !== null) {
            var maxTxt = scoreEl.textContent.split("/")[1] || "";
            scoreEl.textContent = fmt(data.score) + " /" + maxTxt;
          }
          // Sincroniza a nota exibida na sub-aba da pergunta ativa
          var escOcc = (window.CSS && CSS.escape) ? CSS.escape(occurrence) : occurrence;
          var qtabScore = document.querySelector('[data-qtab-score="' + escOcc + '"]') || document.querySelector('[data-qtab-score="' + occurrence + '"]');
          if (qtabScore && data.score !== undefined && data.score !== null) {
            var qParts = qtabScore.textContent.split("/");
            var qMax = qParts[1] ? qParts[1].trim() : "";
            qtabScore.textContent = fmt(data.score) + " / " + qMax;
          }
          // total da dimensao: soma client-side a partir dos cartoes visiveis
          var panel = card ? card.closest("[data-dim-panel]") : null;
          if (panel) {
            var dimName = panel.getAttribute("data-dim-panel");
            var badge = document.querySelector('[data-dim-total="' + dimName + '"]');
            if (badge) badge.textContent = fmt(data.dimension_score);
            var floor = document.querySelector('[data-dim-floor="' + dimName + '"]');
            if (floor) {
              if (data.dimension_meets_minimum === true) floor.textContent = "Piso atendido";
              else if (data.dimension_meets_minimum === false) floor.textContent = "Abaixo do mínimo";
            }
            var subscore = document.querySelector('[data-dim-subscore="' + dimName + '"]');
            if (subscore && data.dimension_score !== undefined && data.dimension_score !== null) {
              subscore.textContent = fmt(data.dimension_score);
            }
          }
          var set = function (id, v) {
            var el = document.getElementById(id);
            if (el) el.textContent = fmt(v);
          };
          set("base-score", data.base_score);
          set("base-score-head", data.base_score);
          set("bonus-avail", data.bonus_available);
          set("bonus-applied", data.bonus_applied);
          set("final-score", data.final_score);
          set("final-score-head", data.final_score);
          var gaugeScore = document.getElementById("gauge-score-val");
          if (gaugeScore) gaugeScore.textContent = fmt(data.final_score) + " / 100 pts";
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
          updateResultSummary(data);
          if (sel) updateStatusSelectColor(sel);
          if (msg) { msg.textContent = "Alteração salva."; msg.style.color = "#16a34a"; }
          toast("Alteração salva.");
        })
        .catch(function (err) {
          console.error("[Salvar] Erro:", err);
          var errMsg;
          if (err instanceof TypeError && (err.message === "Failed to fetch" || err.message === "NetworkError when attempting to fetch resource.")) {
            errMsg = "Servidor não acessível. Verifique se o servidor está rodando (uvicorn app:app --port 8000).";
          } else if (err && err.httpStatus === 409) {
            errMsg = err.message || "DADOS.xlsx está aberto ou bloqueado. Feche a planilha no Excel e tente novamente.";
          } else if (err && err.httpStatus === 422) {
            errMsg = (err.message) ? err.message : "Dados inválidos. Verifique o status selecionado.";
          } else if (err && err.httpStatus === 400) {
            errMsg = (err.message) ? err.message : "Erro na validação dos dados.";
          } else {
            errMsg = (err && err.message) ? err.message : "Não foi possível salvar. Nenhuma alteração foi gravada.";
          }
          if (msg) { msg.textContent = errMsg; msg.style.color = "#dc2626"; }
          toast(errMsg, true);
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

      // 2.1. Interação de clique nos cards de resumo (KPIs)
      var statCards = document.querySelectorAll(".stats .stat[data-stat-filter]");
      if (statCards.length > 0) {
        statCards.forEach(function (card) {
          function handleCardClick() {
            var filterType = card.getAttribute("data-stat-filter");
            var isAlreadyActive = card.classList.contains("is-active");

            statCards.forEach(function (c) { c.classList.remove("is-active"); });

            if (isAlreadyActive || filterType === "all") {
              // Reset: marca todas as opções
              form.querySelectorAll('.ms-dropdown input[type="checkbox"]').forEach(function (cb) { cb.checked = true; });
              if (rangeMin && rangeMax) {
                rangeMin.value = "0";
                rangeMax.value = "100";
                updateRangeSlider();
              }
              if (!isAlreadyActive && filterType === "all") {
                card.classList.add("is-active");
              }
            } else if (filterType === "instituidas") {
              card.classList.add("is-active");
              form.querySelectorAll('.ms-dropdown[data-filter-name="unidade"] input[type="checkbox"]').forEach(function (cb) { cb.checked = true; });
              form.querySelectorAll('.ms-dropdown[data-filter-name="classificacao"] input[type="checkbox"]').forEach(function (cb) { cb.checked = true; });
              form.querySelectorAll('.ms-dropdown[data-filter-name="situacao"] input[type="checkbox"]').forEach(function (cb) {
                cb.checked = (cb.value === "Instituída");
              });
              if (rangeMin && rangeMax) {
                rangeMin.value = "0";
                rangeMax.value = "100";
                updateRangeSlider();
              }
            } else {
              // seguindo, abaixo_dimensao, global_insuficiente, nao_instituida
              card.classList.add("is-active");
              form.querySelectorAll('.ms-dropdown[data-filter-name="unidade"] input[type="checkbox"]').forEach(function (cb) { cb.checked = true; });
              form.querySelectorAll('.ms-dropdown[data-filter-name="situacao"] input[type="checkbox"]').forEach(function (cb) { cb.checked = true; });
              form.querySelectorAll('.ms-dropdown[data-filter-name="classificacao"] input[type="checkbox"]').forEach(function (cb) {
                if (filterType === "nao_instituida") {
                  cb.checked = (cb.value === "nao_instituida" || cb.value === "nao_comprovada");
                } else {
                  cb.checked = (cb.value === filterType);
                }
              });
              if (rangeMin && rangeMax) {
                rangeMin.value = "0";
                rangeMax.value = "100";
                updateRangeSlider();
              }
            }

            // Atualiza triggers das dropdowns
            dropdowns.forEach(function (dd) {
              var trig = dd.querySelector(".ms-trigger");
              var cbs = Array.from(dd.querySelectorAll('input[type="checkbox"]'));
              var checkedCount = cbs.filter(function (c) { return c.checked; }).length;
              var totalCount = cbs.length;
              var textSpan = trig ? trig.querySelector(".ms-trigger-text") : null;
              var name = dd.getAttribute("data-filter-name");
              if (textSpan) {
                if (checkedCount === totalCount) {
                  textSpan.textContent = name === "unidade" ? "Todas as unidades" : name === "situacao" ? "Todas as situações" : "Todas as classificações";
                } else if (checkedCount === 0) {
                  textSpan.textContent = "Nenhum selecionado";
                } else if (checkedCount === 1) {
                  var sel = cbs.find(function (c) { return c.checked; });
                  var lbl = sel ? sel.closest(".ms-option").querySelector(".ms-option-label") : null;
                  textSpan.textContent = lbl ? lbl.textContent.trim() : "1 selecionado";
                } else {
                  textSpan.textContent = checkedCount + " selecionados";
                }
              }
            });

            form.dispatchEvent(new Event("filter-change"));
          }

          card.addEventListener("click", handleCardClick);
          card.addEventListener("keydown", function (e) {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
              handleCardClick();
            }
          });
        });
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
