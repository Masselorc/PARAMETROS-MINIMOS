"""Snapshot estatico das paginas p/ GitHub Pages, COM valores reais calculados.

Gera docs/index.html (Visao Geral), docs/unidades.html, docs/metodologia.html
e docs/relatorios.html a partir dos templates Jinja2 + DADOS.xlsx commitado.
Le a planilha via src.workbook_service.read_summary (somente leitura) e
imprime notas, barras da nota final, classificacoes e cards reais.
Sem backend interativo: links de avaliacao/anexos/relatorios nao funcionam
no snapshot (apenas exibicao).
Uso: python tools/build_pages.py
"""
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DOCS = BASE / "docs"

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
except ImportError as exc:
    raise SystemExit("jinja2 nao instalado. Rode: pip install jinja2") from exc
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
    "Página estática de demonstração com os valores calculados em {stamp} — "
    "o sistema completo roda localmente "
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

    import sys
    sys.path.insert(0, str(BASE))
    from src.workbook_service import read_summary

    rows, cards = read_summary()  # somente leitura do DADOS.xlsx commitado
    stamp = datetime.now().strftime("%d/%m/%Y %H:%M")

    def _uf_flag(k: str) -> str:
        return "es" if k.startswith("ES_") else k.lower()

    units = [{"entity_key": r["entity_key"], "uf": r["uf"],
              "flag": r.get("flag") or _uf_flag(r["entity_key"]),
              "unidade_label": r["unidade_label"]}
             for r in rows]

    pages = {
        "index.html": ("dashboard.html", {"request": Req(), "rows": rows, "cards": cards, "filters": {"q": "", "situacao": "", "classificacao": "", "nota_min": "", "nota_max": ""}}),
        "unidades.html": ("units.html", {"request": Req(), "rows": rows, "filters": {"q": "", "situacao": "", "classificacao": "", "nota_min": "", "nota_max": ""}}),
        "relatorios.html": ("reports.html", {"request": Req(), "units": units}),
        "metodologia.html": ("methodology.html", {"request": Req()}),
    }
    for fname, (tpl, ctx) in pages.items():
        html = env.get_template(tpl).render(ctx)
        # nav ativa do snapshot
        html = html.replace('href="/static/app.css"', 'href="app.css"').replace("href='/static/app.css'", 'href="app.css"')
        html = html.replace('src="/static/app.js"', 'src="app.js"').replace("src='/static/app.js'", 'src="app.js"')
        banner = f'<div class="section"><div class="section-body"><p class="muted">{STATIC_NOTE.format(stamp=stamp)}</p></div></div>'
        html = html.replace('<main id="main" tabindex="-1">', '<main id="main" tabindex="-1">' + banner, 1)
        (DOCS / fname).write_text(html, encoding="utf-8")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Snapshot gerado em {DOCS} ({len(pages)} páginas) com valores reais de {stamp}.")


if __name__ == "__main__":
    main()
