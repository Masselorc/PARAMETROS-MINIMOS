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
          var set = function (id, v) {
            var el = document.getElementById(id);
            if (el) el.textContent = fmt(v);
          };
          set("base-score", data.base_score);
          set("bonus-avail", data.bonus_available);
          set("bonus-applied", data.bonus_applied);
          set("final-score", data.final_score);
          var cls = document.getElementById("classification");
          if (cls && data.classification) cls.textContent = data.classification;
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
