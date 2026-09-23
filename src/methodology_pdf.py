"""Converte o conteúdo da página de metodologia em anexo para os PDFs."""
from __future__ import annotations

from dataclasses import dataclass, field
from html import escape
from html.parser import HTMLParser

from jinja2 import Environment, FileSystemLoader, select_autoescape
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Image, PageBreak, Paragraph, Spacer, Table, TableStyle

from .config import BASE_DIR
from .workbook_service import read_methodology_matrix


@dataclass
class _Node:
    tag: str
    attrs: dict[str, str] = field(default_factory=dict)
    children: list[_Node | str] = field(default_factory=list)

    def has_class(self, name: str) -> bool:
        return name in self.attrs.get("class", "").split()


class _TreeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = _Node("root")
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = _Node(tag, dict(attrs))
        self.stack[-1].children.append(node)
        if tag not in {"br", "img", "meta", "link", "input", "hr"}:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.stack[-1].children.append(_Node(tag, dict(attrs)))

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                return

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def _nodes(parent: _Node, tag: str | None = None) -> list[_Node]:
    return [child for child in parent.children if isinstance(child, _Node) and (tag is None or child.tag == tag)]


def _find(parent: _Node, predicate) -> _Node | None:
    for child in _nodes(parent):
        if predicate(child):
            return child
        found = _find(child, predicate)
        if found is not None:
            return found
    return None


def _inline(node: _Node | str) -> str:
    if isinstance(node, str):
        return escape(node)
    content = "".join(_inline(child) for child in node.children)
    if node.tag in {"b", "strong"}:
        return f"<b>{content}</b>"
    if node.tag in {"i", "em"}:
        return f"<i>{content}</i>"
    if node.tag == "u":
        return f"<u>{content}</u>"
    if node.tag == "br":
        return "<br/>"
    if node.tag == "span" and node.has_class("cell-sub"):
        return f'<br/><font color="#526572">{content}</font>'
    if node.tag == "a" and node.attrs.get("href"):
        href = escape(node.attrs["href"], quote=True)
        return f'<a href="{href}" color="#155b67">{content}</a>'
    return content


def _markup(node: _Node) -> str:
    return "".join(_inline(child) for child in node.children).strip()


def _table_flow(node: _Node, styles: dict) -> Table:
    rows: list[list] = []
    spans: list[tuple[int, int, int]] = []
    header_rows = 0
    footer_rows: list[int] = []
    for group in _nodes(node):
        if group.tag not in {"thead", "tbody", "tfoot"}:
            continue
        for tr in _nodes(group, "tr"):
            row = []
            for cell in _nodes(tr):
                if cell.tag not in {"th", "td"}:
                    continue
                start = len(row)
                markup = _markup(cell) or " "
                if cell.tag == "th":
                    markup = f"<b>{markup}</b>"
                row.append(Paragraph(markup, styles["cell"]))
                colspan = max(1, int(cell.attrs.get("colspan", "1")))
                row.extend([""] * (colspan - 1))
                if colspan > 1:
                    spans.append((len(rows), start, start + colspan - 1))
            if row:
                rows.append(row)
                if group.tag == "thead":
                    header_rows += 1
                elif group.tag == "tfoot":
                    footer_rows.append(len(rows) - 1)
    if not rows:
        raise ValueError("Tabela vazia na metodologia.")
    columns = max(len(row) for row in rows)
    for row in rows:
        row.extend([""] * (columns - len(row)))
    widths = [180 * mm / columns] * columns
    if columns == 2:
        widths = [115 * mm, 65 * mm]
    elif columns == 3:
        widths = [22 * mm, 132 * mm, 26 * mm]
    commands = [
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C8D2D7")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if header_rows:
        commands.extend([
            ("BACKGROUND", (0, 0), (-1, header_rows - 1), colors.HexColor("#EAF2F4")),
            ("FONTNAME", (0, 0), (-1, header_rows - 1), "Helvetica-Bold"),
        ])
    for row_number in footer_rows:
        commands.append(("BACKGROUND", (0, row_number), (-1, row_number), colors.HexColor("#F4F6F7")))
    for row_number, first, last in spans:
        commands.append(("SPAN", (first, row_number), (last, row_number)))
    result = Table(rows, colWidths=widths, repeatRows=header_rows, hAlign="LEFT")
    result.setStyle(TableStyle(commands))
    return result


def _block_flow(node: _Node, styles: dict) -> list:
    if node.tag in {"p", "h2", "h3"}:
        style = styles[{"p": "body", "h2": "heading", "h3": "subheading"}[node.tag]]
        return [Paragraph(_markup(node), style)]
    if node.tag in {"ul", "ol"}:
        flows = []
        for index, item in enumerate(_nodes(node, "li"), start=1):
            marker = f"{index}. " if node.tag == "ol" else "- "
            flows.append(Paragraph(marker + _markup(item), styles["list"]))
        return flows
    if node.tag == "table":
        return [_table_flow(node, styles), Spacer(1, 1.5 * mm)]
    if node.tag == "div" and node.has_class("info"):
        paragraphs = _nodes(node, "p")
        if paragraphs:
            return [Paragraph(_markup(child), styles["note"]) for child in paragraphs]
        return [Paragraph(_markup(node), styles["note"])]
    flows = []
    for child in _nodes(node):
        flows.extend(_block_flow(child, styles))
    return flows


def _methodology_tree() -> _Node:
    env = Environment(loader=FileSystemLoader(str(BASE_DIR / "templates")), autoescape=select_autoescape())
    env.globals["url_for"] = lambda name, **kwargs: kwargs.get("path", "")
    html = env.get_template("methodology.html").render({
        "read_only": True,
        "methodology_dimensions": read_methodology_matrix(),
    })
    parser = _TreeParser()
    parser.feed(html)
    report = _find(parser.root, lambda node: node.tag == "div" and node.has_class("report"))
    if report is None:
        raise ValueError("Conteúdo da metodologia não encontrado no template.")
    return report


def methodology_flow(styles, logo_path, sei_processo_url: str, in_75_url: str) -> list:
    """Inclui integralmente as seções exibidas na página de metodologia."""
    pdf_styles = {
        "title": ParagraphStyle("MethodologyTitle", parent=styles["Normal"], alignment=TA_CENTER,
                                fontName="Helvetica-Bold", fontSize=11, leading=14,
                                textColor=colors.HexColor("#103E49")),
        "reference": ParagraphStyle("MethodologyReference", parent=styles["Normal"], alignment=TA_CENTER,
                                    fontSize=7, leading=10, textColor=colors.HexColor("#526572")),
        "heading": ParagraphStyle("MethodologyHeading", parent=styles["Heading2"], fontName="Helvetica-Bold",
                                  fontSize=10, leading=13, spaceBefore=4 * mm, spaceAfter=1.5 * mm,
                                  keepWithNext=True, textColor=colors.HexColor("#103E49")),
        "subheading": ParagraphStyle("MethodologySubheading", parent=styles["Heading3"], fontName="Helvetica-Bold",
                                     fontSize=8.5, leading=11, spaceBefore=2.5 * mm, spaceAfter=1 * mm,
                                     keepWithNext=True, textColor=colors.HexColor("#103E49")),
        "body": ParagraphStyle("MethodologyBody", parent=styles["Normal"], fontSize=8, leading=11,
                               spaceAfter=1.8 * mm, alignment=TA_JUSTIFY,
                               textColor=colors.HexColor("#192E39")),
        "list": ParagraphStyle("MethodologyList", parent=styles["Normal"], fontSize=8, leading=11,
                               leftIndent=8 * mm, firstLineIndent=-4 * mm, spaceAfter=1 * mm,
                               textColor=colors.HexColor("#192E39")),
        "cell": ParagraphStyle("MethodologyCell", parent=styles["Normal"], fontSize=7.2, leading=9.5,
                               textColor=colors.HexColor("#192E39")),
        "note": ParagraphStyle("MethodologyNote", parent=styles["Normal"], fontSize=7.5, leading=10.5,
                               spaceBefore=1 * mm, spaceAfter=1 * mm, backColor=colors.HexColor("#EDF5F6"),
                               borderPadding=5, textColor=colors.HexColor("#103E49")),
    }
    flows = [PageBreak()]
    if logo_path.exists():
        logo_width = 60 * mm
        image = Image(str(logo_path), width=logo_width, height=logo_width * 197 / 1342)
        image.hAlign = "CENTER"
        flows.extend([image, Spacer(1, 2 * mm)])
    flows.extend([
        Paragraph("ANEXO - METODOLOGIA DE MONITORAMENTO DOS PARÂMETROS MÍNIMOS DAS OUVIDORIAS DE SERVIÇOS PENAIS", pdf_styles["title"]),
        Spacer(1, 1.5 * mm),
        Paragraph(f'Referência: Processo <a href="{sei_processo_url}">SEI nº 08016.027689/2025-19</a> · '
                  f'<a href="{in_75_url}">IN GABSEC/SENAPPEN/MJSP nº 75/2026</a> · Doc. SEI 37070578',
                  pdf_styles["reference"]),
        Spacer(1, 3 * mm),
    ])
    report = _methodology_tree()
    sections = [node for node in _nodes(report, "section") if node.has_class("section")]
    if not sections:
        raise ValueError("Nenhuma seção de metodologia encontrada para o PDF.")
    for section in sections:
        for child in _nodes(section):
            flows.extend(_block_flow(child, pdf_styles))
    return flows
