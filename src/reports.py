"""Relatorios PDF (ReportLab) e XLSX (openpyxl) — gerais e individuais."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Font
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from .config import (
    BASE_WEIGHTS,
    DIMENSION_MINIMUMS,
    DIMENSION_NAMES,
    EXPORTACOES_DIR,
    GLOBAL_BASE_MINIMUM,
    WORKBOOK_FILENAME,
)
from .workbook_service import read_unit_detail

HEADER_LINES = [
    "MINISTÉRIO DA JUSTIÇA E SEGURANÇA PÚBLICA",
    "SECRETARIA NACIONAL DE POLÍTICAS PENAIS",
    "OUVIDORIA NACIONAL DE SERVIÇOS PENAIS",
    "MONITORAMENTO DOS PARÂMETROS MÍNIMOS DAS OUVIDORIAS DE SERVIÇOS PENAIS",
]
NOTA_METODOLOGICA = (
    "As pontuações, pesos e faixas de classificação constituem metodologia "
    "de monitoramento da ONASP e não integram o texto da Instrução Normativa "
    "GABSEC/SENAPPEN/MJSP nº 75/2026. A avaliação deve ser interpretada em "
    "conjunto com as evidências registradas no sistema."
)


def _stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _base_doc(path: Path, title: str) -> tuple[SimpleDocTemplate, list, dict]:
    EXPORTACOES_DIR.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(path), pagesize=A4, title=title,
                            leftMargin=15 * mm, rightMargin=15 * mm,
                            topMargin=15 * mm, bottomMargin=15 * mm)
    styles = getSampleStyleSheet()
    return doc, [], styles


def _header_flow(styles) -> list:
    flows = []
    for line in HEADER_LINES:
        flows.append(Paragraph(f"<b>{line}</b>", styles["Normal"]))
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    flows.append(Paragraph(
        f"Referência: IN GABSEC/SENAPPEN/MJSP nº 75/2026 — metodologia ONASP. "
        f"Dados: {WORKBOOK_FILENAME}. Gerado em {now}.", styles["Normal"]))
    flows.append(Spacer(1, 6 * mm))
    return flows


def _table_style() -> TableStyle:
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17365D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ])


def generate_general_pdf(rows: list[dict], cards: dict) -> Path:
    path = EXPORTACOES_DIR / f"relatorio_geral_{_stamp()}.pdf"
    doc, story, styles = _base_doc(path, "Relatório geral — Parâmetros Mínimos")
    story.extend(_header_flow(styles))
    story.append(Paragraph("<b>Síntese</b>", styles["Heading2"]))
    story.append(Paragraph(
        f"Unidades avaliadas: {cards['unidades']}. Ouvidorias instituídas: {cards['instituidas']}. "
        f"Não instituídas: {cards['nao_instituidas']}. Instituição não comprovada: {cards['nao_comprovadas']}. "
        f"Seguindo os parâmetros mínimos: {cards['seguindo_minimos']}. "
        f"Abaixo do mínimo em dimensão essencial: {cards['abaixo_dimensao']}. "
        f"Aderência global insuficiente: {cards['global_insuficiente']}.",
        styles["Normal"]))
    story.append(Spacer(1, 4 * mm))
    data = [["UF", "Unidade", "Inst", "Aut", "Imp", "Aces", "Trans", "Integ",
             "Base", "Bônus", "Final", "Classificação"]]
    for r in rows:
        d = r["dim"]
        data.append([
            r["uf"], r["unidade_label"][:40],
            _fmt(d.get("01_Institucionalização")), _fmt(d.get("02_Autonomia")),
            _fmt(d.get("03_Imparcialidade")), _fmt(d.get("04_Acessibilidade")),
            _fmt(d.get("05_Transparência")), _fmt(d.get("06_Integração Tec")),
            _fmt(r["base_score"]), _fmt(r["bonus_applied"]), _fmt(r["final_score"]),
            (r["classification"] or "")[:60],
        ])
    t = Table(data, repeatRows=1)
    t.setStyle(_table_style())
    story.append(t)
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(f"<i>{NOTA_METODOLOGICA}</i>", styles["Normal"]))
    doc.build(story)
    return path


def generate_unit_pdf(entity_key: str) -> Path:
    detail = read_unit_detail(entity_key)
    ent = detail["entity"]
    res = detail["result"]
    path = EXPORTACOES_DIR / f"relatorio_{entity_key}_{_stamp()}.pdf"
    doc, story, styles = _base_doc(path, f"Relatório individual — {entity_key}")
    story.extend(_header_flow(styles))
    story.append(Paragraph(
        f"<b>UF:</b> {ent['uf']} &nbsp; <b>Unidade:</b> {ent['unidade_label']} &nbsp; "
        f"<b>Situação:</b> {res['situacao']} &nbsp; "
        f"<b>Emitido em:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles["Normal"]))
    story.append(Paragraph("<b>Resultado</b>", styles["Heading2"]))
    dimension_results = " | ".join(
        f"{dim['dimension_name']}: {_fmt(res['dim_scores'].get(dim['sheet_name']))}"
        + (f" (mínimo {DIMENSION_MINIMUMS[dim['sheet_name']]:g})"
           if dim["sheet_name"] in DIMENSION_MINIMUMS else "")
        for dim in detail["dimensions"]
        if dim["sheet_name"] in BASE_WEIGHTS
    )
    story.append(Paragraph(
        f"{dimension_results} | "
        f"Nota-base (parâmetros mínimos, mínimo {GLOBAL_BASE_MINIMUM}): {_fmt(res['base_score'])} | "
        f"Bônus disponível: {_fmt(res['bonus_available'])} | "
        f"Bônus aplicado: {_fmt(res['bonus_applied'])} | Nota final: {_fmt(res['final_score'])} | "
        f"Segue os parâmetros mínimos: {'Sim' if res['meets_minimum_parameters'] else 'Não'} | "
        f"Classificação: {res['classification']}", styles["Normal"]))
    for dim in detail["dimensions"]:
        story.append(Paragraph(f"<b>{dim['dimension_name']}</b>", styles["Heading3"]))
        qdata = []
        for q in dim["questions"]:
            docs = ", ".join(a["original_filename"] for a in q["attachments"]) or "—"
            qdata.append([
                Paragraph(f"<b>{q['question_code']}</b><br/>{q['question_title'][:200]}"
                          f"<br/>Item: {q['item_name'][:120]}", styles["Normal"]),
                Paragraph(f"Resp: {(q['resposta'] or '')[:500]}<br/>Fund: {q['fundamentacao'][:200]}"
                          f"<br/>Aval: {q['status']} ({q['score']}/{q['max_display']})"
                          f"<br/>Evid: {(q['evidence_text'] or '')[:500]}"
                          f"<br/>Docs: {docs[:300]}", styles["Normal"]),
            ])
        if qdata:
            t = Table([["Pergunta", "Detalhe"]] + qdata, colWidths=[55 * mm, 115 * mm], repeatRows=1)
            t.setStyle(_table_style())
            story.append(t)
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(f"<i>{NOTA_METODOLOGICA}</i>", styles["Normal"]))
    doc.build(story)
    return path


def _fmt(v) -> str:
    if v is None:
        return "—"
    try:
        f = float(v)
        return f"{f:g}"
    except (TypeError, ValueError):
        return str(v)


def generate_general_xlsx(rows: list[dict], cards: dict) -> Path:
    EXPORTACOES_DIR.mkdir(parents=True, exist_ok=True)
    path = EXPORTACOES_DIR / f"relatorio_geral_{_stamp()}.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Resumo"
    ws.append(["Métrica", "Valor"])
    for k, v in cards.items():
        ws.append([k, v])
    ws2 = wb.create_sheet("Resultados por unidade")
    ws2.append(["UF", "Unidade"]
               + [DIMENSION_NAMES[sheet] for sheet in BASE_WEIGHTS]
               + ["Nota-base", "Bônus", "Nota final", "Classificação"])
    for r in rows:
        d = r["dim"]
        ws2.append([r["uf"], r["unidade_label"]]
                   + [d.get(sheet) for sheet in BASE_WEIGHTS]
                   + [
                    r["base_score"], r["bonus_applied"], r["final_score"],
                    r["classification"]])
    ws3 = wb.create_sheet("Metodologia resumida")
    ws3.append(["Nota", NOTA_METODOLOGICA])
    for wsx in (ws, ws2, ws3):
        for cell in wsx[1]:
            cell.font = Font(bold=True)
    wb.save(str(path))
    return path


def generate_unit_xlsx(entity_key: str) -> Path:
    detail = read_unit_detail(entity_key)
    ent = detail["entity"]
    res = detail["result"]
    EXPORTACOES_DIR.mkdir(parents=True, exist_ok=True)
    path = EXPORTACOES_DIR / f"relatorio_{entity_key}_{_stamp()}.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Resumo"
    ws.append(["Campo", "Valor"])
    for k in ("situacao", "base_score", "bonus_available", "bonus_applied",
              "final_score", "meets_minimum_parameters", "classification"):
        ws.append([k, res.get(k)])
    ws.append(["global_base_minimum", GLOBAL_BASE_MINIMUM])
    for sheet in BASE_WEIGHTS:
        ws.append([f"minimo_{sheet}", DIMENSION_MINIMUMS.get(sheet, "")])
    ws.append(["uf", ent["uf"]])
    ws.append(["unidade", ent["unidade_label"]])
    ws.append(["nota_metodologica", NOTA_METODOLOGICA])
    ws2 = wb.create_sheet("Avaliação detalhada")
    ws2.append(["Dimensão", "Código", "Pergunta", "Item", "Resposta do diagnóstico",
                "Fundamentação", "Avaliação", "Pontuação", "Evidência"])
    for dim in detail["dimensions"]:
        for q in dim["questions"]:
            ws2.append([dim["dimension_name"], q["question_code"], q["question_title"], q["item_name"],
                        q["resposta"], q["fundamentacao"], q["status"],
                        q["score"], q["evidence_text"]])
    ws3 = wb.create_sheet("Anexos")
    ws3.append(["Pergunta", "Arquivo", "Tamanho", "SHA-256", "Ativo"])
    for dim in detail["dimensions"]:
        for q in dim["questions"]:
            for a in q["attachments"]:
                ws3.append([q["occurrence_key"], a["original_filename"],
                            a["size_bytes"], a["sha256"], "TRUE"])
    for c in ws2.columns:
        pass
    for wsx in (ws, ws2, ws3):
        wsx.sheet_view.showGridLines = True
        for cell in wsx[1]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(wrap_text=True, vertical="top")
    wb.save(str(path))
    return path
