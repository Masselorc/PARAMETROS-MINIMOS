"""Snapshot estatico das paginas institucionais p/ GitHub Pages.

Gera docs/index.html (Visao Geral), docs/unidades.html, docs/metodologia.html
e docs/relatorios.html a partir dos templates Jinja2, SEM backend e SEM DADOS.xlsx.
Nao executa scoring nem le a planilha: usa cards zerados e lista fixa de UFs.
Uso: python tools/build_pages.py
"""
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DOCS = BASE / "docs"

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
except ImportError as exc:
    raise SystemExit("jinja2 nao instalado. Rode: pip install jinja2") from exc

UFS = [
    ("AC", "Acre"), ("AL", "Alagoas"), ("AP", "Amapá"), ("AM", "Amazonas"),
    ("BA", "Bahia"), ("CE", "Ceará"), ("DF", "Distrito Federal"),
    ("ES_PP", "Espírito Santo — Polícia Penal"),
    ("ES_SEJUS", "Espírito Santo — SEJUS/ES"),
    ("GO", "Goiás"), ("MA", "Maranhão"), ("MT", "Mato Grosso"),
    ("MS", "Mato Grosso do Sul"), ("MG", "Minas Gerais"), ("PA", "Pará"),
    ("PB", "Paraíba"), ("PR", "Paraná"), ("PE", "Pernambuco"), ("PI", "Piauí"),
    ("RJ", "Rio de Janeiro"), ("RN", "Rio Grande do Norte"),
    ("RS", "Rio Grande do Sul"), ("RO", "Rondônia"), ("RR", "Roraima"),
    ("SC", "Santa Catarina"), ("SP", "São Paulo"), ("SE", "Sergipe"),
    ("TO", "Tocantins"),
]

STATIC_NOTE = (
    "Página estática de demonstração — o sistema completo roda localmente "
    "(uvicorn app:app --host 127.0.0.1 --port 8000) com leitura/edição do DADOS.xlsx."
)


def _url_for(name, **kw):
    path = kw.get("path", "")
    if path == "app.css":
        return "app.css"
    if path == "app.js":
        return "app.js"
    if path.startswith("bandeiras/"):
        return path  # docs/bandeiras/*.svg copiados abaixo
    return path


def main() -> None:
    env = Environment(
        loader=FileSystemLoader(str(BASE / "templates")),
        autoescape=select_autoescape(),
    )
    # url_for inexistente no modo estatico
    env.globals["url_for"] = _url_for

    class Req:
        url = type("U", (), {"path": "/"})()

    DOCS.mkdir(exist_ok=True)
    css_src = BASE / "static" / "app.css"
    if css_src.exists():
        (DOCS / "app.css").write_bytes(css_src.read_bytes())
    (DOCS / "app.js").write_text("// snapshot estático: sem interações de backend.\n", encoding="utf-8")
    import shutil
    flags_src = BASE / "static" / "bandeiras"
    if flags_src.exists():
        shutil.copytree(flags_src, DOCS / "bandeiras", dirs_exist_ok=True)

    cards = {"unidades": 28, "instituidas": "—", "nao_instituidas": "—",
             "nao_comprovadas": "—", "seguindo_minimos": "—",
             "abaixo_dimensao": "—", "global_insuficiente": "—"}

    def _uf_flag(k: str) -> str:
        return "es" if k.startswith("ES_") else k.lower()

    rows = [{"uf": (k if not k.startswith("ES_") else "ES"), "flag": _uf_flag(k),
             "unidade_label": lab,
             "entity_key": k, "inst": None, "aut": None, "imp": None, "aces": None,
             "trans": None, "integ": None, "base_score": None, "bonus_applied": None,
             "final_score": None, "classification": "Snapshot estático",
             "situacao": "Snapshot estático"}
            for k, lab in UFS]
    filters = {"q": "", "situacao": "", "classificacao": "", "nota_min": "", "nota_max": ""}
    units = [{"entity_key": k, "uf": (k if not k.startswith("ES_") else "ES"),
              "flag": _uf_flag(k), "unidade_label": lab}
             for k, lab in UFS]

    pages = {
        "index.html": ("dashboard.html", {"request": Req(), "rows": rows, "cards": cards, "filters": filters}),
        "unidades.html": ("units.html", {"request": Req(), "rows": rows, "filters": filters}),
        "relatorios.html": ("reports.html", {"request": Req(), "units": units}),
        "metodologia.html": ("methodology.html", {"request": Req()}),
    }
    for fname, (tpl, ctx) in pages.items():
        html = env.get_template(tpl).render(ctx)
        # nav ativa do snapshot
        html = html.replace('href="/static/app.css"', 'href="app.css"').replace("href='/static/app.css'", 'href="app.css"')
        html = html.replace('src="/static/app.js"', 'src="app.js"').replace("src='/static/app.js'", 'src="app.js"')
        banner = f'<div class="section"><div class="section-body"><p class="muted">{STATIC_NOTE}</p></div></div>'
        html = html.replace('<main id="main" tabindex="-1">', '<main id="main" tabindex="-1">' + banner, 1)
        (DOCS / fname).write_text(html, encoding="utf-8")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Snapshot gerado em {DOCS} ({len(pages)} páginas).")


if __name__ == "__main__":
    main()
