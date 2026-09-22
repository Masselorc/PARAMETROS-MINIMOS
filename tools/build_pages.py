"""Gera a versão somente de consulta da aplicação para o GitHub Pages.

Renderiza as quatro páginas gerais, uma página de detalhe por unidade e
relatórios PDF/XLSX estáticos usando o DADOS.xlsx commitado. A edição fica
somente na aplicação FastAPI local.
Uso: python tools/build_pages.py
"""
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

BASE = Path(__file__).resolve().parent.parent
DOCS = BASE / "docs"

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
except ImportError as exc:
    raise SystemExit("jinja2 nao instalado. Rode: pip install jinja2") from exc

STATIC_NOTE = (
    "Snapshot de consulta atualizado em {stamp}, gerado a partir do DADOS.xlsx. "
    "Edição e gravação permanecem disponíveis somente no sistema local."
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


def _render(env, template_name: str, context: dict, destination: Path, stamp: str) -> None:
    html = env.get_template(template_name).render(context)
    banner = (
        '<div class="section"><div class="section-body"><p class="muted">'
        f'{STATIC_NOTE.format(stamp=stamp)}</p></div></div>'
    )
    html = html.replace('<main id="main" tabindex="-1">',
                        '<main id="main" tabindex="-1">' + banner, 1)
    html = "\n".join(line.rstrip() for line in html.splitlines()) + "\n"
    destination.write_text(html, encoding="utf-8")


def _copy_static_attachments(detail: dict) -> None:
    """Copy only active attachment files under ANEXOS into the static snapshot."""
    import shutil

    annex_root = (BASE / "ANEXOS").resolve()
    if not annex_root.exists():
        return
    for dimension in detail["dimensions"]:
        for question in dimension["questions"]:
            for attachment in question["attachments"]:
                source = (BASE / attachment.get("relative_path", "")).resolve()
                try:
                    relative = source.relative_to(annex_root)
                except ValueError:
                    continue
                if not source.is_file():
                    continue
                target_relative = Path("anexos") / relative
                target = DOCS / target_relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
                attachment["static_url"] = target_relative.as_posix()


def _generate_static_reports(rows: list[dict], cards: dict, units: list[dict]) -> dict:
    """Generate report downloads into temporary exports, then copy to docs/."""
    import shutil

    import src.reports as report_service

    reports_dir = DOCS / "relatorios"
    reports_dir.mkdir(parents=True, exist_ok=True)
    original_export_dir = report_service.EXPORTACOES_DIR
    with TemporaryDirectory(prefix="pages_reports_") as temp_dir:
        report_service.EXPORTACOES_DIR = Path(temp_dir)
        def _safe_copy(src, dst):
            try:
                shutil.copy2(src, dst)
            except OSError as err:
                if getattr(err, "winerror", None) == 1224 or "1224" in str(err):
                    pass
                else:
                    raise

        try:
            general_pdf = report_service.generate_general_pdf(rows, cards)
            general_xlsx = report_service.generate_general_xlsx(rows, cards)
            _safe_copy(general_pdf, reports_dir / "geral.pdf")
            _safe_copy(general_xlsx, reports_dir / "geral.xlsx")
            for unit in units:
                entity_key = unit["entity_key"]
                pdf = report_service.generate_unit_pdf(entity_key)
                xlsx = report_service.generate_unit_xlsx(entity_key)
                _safe_copy(pdf, reports_dir / f"unidade-{entity_key}.pdf")
                _safe_copy(xlsx, reports_dir / f"unidade-{entity_key}.xlsx")
        finally:
            report_service.EXPORTACOES_DIR = original_export_dir
    return {
        "general_pdf": "relatorios/geral.pdf",
        "general_xlsx": "relatorios/geral.xlsx",
    }


def main() -> None:
    env = Environment(
        loader=FileSystemLoader(str(BASE / "templates")),
        autoescape=select_autoescape(),
    )
    # url_for inexistente no modo estatico
    env.globals["url_for"] = _url_for

    class Req:
        def __init__(self, path: str):
            self.url = type("U", (), {"path": path})()

    DOCS.mkdir(exist_ok=True)
    css_src = BASE / "static" / "app.css"
    if css_src.exists():
        (DOCS / "app.css").write_bytes(css_src.read_bytes())
    import shutil
    static_js = BASE / "static" / "pages.js"
    if static_js.exists():
        shutil.copy2(static_js, DOCS / "app.js")
    table_sort_js = BASE / "static" / "table-sort.js"
    if table_sort_js.exists():
        shutil.copy2(table_sort_js, DOCS / "table-sort.js")
    flags_src = BASE / "static" / "bandeiras"
    if flags_src.exists():
        shutil.copytree(flags_src, DOCS / "bandeiras", dirs_exist_ok=True)

    import sys
    sys.path.insert(0, str(BASE))
    from src.config import BASE_WEIGHTS, DIMENSION_MINIMUMS
    from src.workbook_service import read_all_unit_details, read_summary, read_unit_detail

    rows, cards = read_summary()  # somente leitura do DADOS.xlsx commitado
    all_details = read_all_unit_details()
    stamp = datetime.now().strftime("%d/%m/%Y %H:%M")
    classification_keys = {
        "Instituída — seguindo os parâmetros mínimos": "seguindo",
        "Instituída — abaixo do mínimo em dimensão essencial": "abaixo_dimensao",
        "Instituída — aderência global insuficiente": "global_insuficiente",
        "Não instituída": "nao_instituida",
        "Instituição não comprovada": "nao_comprovada",
    }

    def _uf_flag(k: str) -> str:
        return "es" if k.startswith("ES_") else k.lower()

    for row in rows:
        row["classification_key"] = classification_keys.get(row["classification"], "")
        row["static_page"] = f"unidade-{row['entity_key']}.html"
        row["flag"] = row.get("flag") or _uf_flag(row["entity_key"])
    units = [
        {"entity_key": row["entity_key"], "uf": row["uf"],
         "flag": row["flag"], "unidade_label": row["unidade_label"],
         "situacao": row["situacao"], "final_score": row["final_score"],
         "classification": row["classification"],
         "classification_key": row["classification_key"],
         "static_page": row["static_page"],
         "static_pdf": f"relatorios/unidade-{row['entity_key']}.pdf",
         "static_xlsx": f"relatorios/unidade-{row['entity_key']}.xlsx"}
        for row in rows
    ]
    static_reports = _generate_static_reports(rows, cards, units)
    static_reports["stamp"] = stamp

    pages = {
        "index.html": ("dashboard.html", {"request": Req("/"), "static_page": "index.html", "read_only": True, "rows": rows, "cards": cards, "filters": {"q": "", "situacao": "", "classificacao": "", "nota_min": "", "nota_max": ""}}),
        "unidades.html": ("units.html", {"request": Req("/unidades"), "static_page": "unidades.html", "read_only": True, "rows": rows, "filters": {"q": "", "situacao": "", "classificacao": "", "nota_min": "", "nota_max": ""}}),
        "relatorios.html": ("reports.html", {
            "request": Req("/relatorios"),
            "static_page": "relatorios.html",
            "read_only": True,
            "units": units,
            "rows": rows,
            "cards": cards,
            "all_details": all_details,
            "selected_key": units[0]["entity_key"] if units else "AC",
            "static_reports": static_reports,
            "base_weights": BASE_WEIGHTS,
            "dimension_minimums": DIMENSION_MINIMUMS,
        }),
        "metodologia.html": ("methodology.html", {"request": Req("/metodologia"), "static_page": "metodologia.html", "read_only": True}),
    }
    for fname, (tpl, ctx) in pages.items():
        _render(env, tpl, ctx, DOCS / fname, stamp)

    for unit in units:
        detail = all_details.get(unit["entity_key"]) or read_unit_detail(unit["entity_key"])
        _copy_static_attachments(detail)
        filename = unit["static_page"] if "static_page" in unit else f"unidade-{unit['entity_key']}.html"
        _render(env, "unit_detail.html", {
            "request": Req("/unidades/" + unit["entity_key"]),
            "static_page": filename,
            "read_only": True,
            "entity": detail["entity"],
            "dimensions": detail["dimensions"],
            "result": detail["result"],
        }, DOCS / filename, stamp)

    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Snapshot gerado em {DOCS} ({len(pages) + len(units)} páginas, {len(units)} relatórios individuais) com valores reais de {stamp}.")


if __name__ == "__main__":
    main()
