"""Servico de leitura/gravacao segura do DADOS.xlsx.

Regras (especificacao secao 9):
1. adquirir lock (.dados.lock via filelock);
2. criar backup em BACKUPS/DADOS_YYYYMMDD_HHMMSS.xlsx;
3. carregar DADOS.xlsx;
4. aplicar alteracao;
5. salvar em arquivo temporario;
6. reabrir o temporario para validar que e XLSX legivel;
7. substituir DADOS.xlsx;
8. liberar lock.

Nunca usar letras fixas de coluna: parser detecta perguntas pelos
codigos M*-* na linha 5 e resolve colunas por deslocamento logico.
"""
from __future__ import annotations

import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any

import openpyxl
from filelock import FileLock, Timeout

from .config import (
    ANEXOS_DIR,
    BACKUPS_DIR,
    BASE_WEIGHTS,
    BONUS_MAX,
    DB_ANEXOS_HEADERS,
    DB_AUDITORIA_HEADERS,
    DB_EVIDENCIAS_HEADERS,
    DIMENSION_NAMES,
    DIMENSION_SHEETS,
    EVIDENCE_INITIAL_TEXT,
    EXPECTED_SHEETS,
    EXPORTACOES_DIR,
    LOCK_PATH,
    WORKBOOK_PATH,
)
from .scoring import (
    classify,
    score_bonus_item,
    score_institutional,
    score_ordinary,
    situacao_from_status,
)

CODE_RE = re.compile(r"M\d+-\d+")
WEIGHT_RE = re.compile(r"([\d]+(?:[.,]\d+)?)")
BONUS_RE = re.compile(r"\(\+(\d+(?:[.,]\d+)?)\)")

DATA_START_ROW = 7
DATA_END_ROW = 34
RESUMO_START_ROW = 5

ORDINARY_STATUSES = ("Atende", "Parcial", "Não atende", "Sem evidência")
INSTITUTIONAL_STATUSES = ("Sim", "Não", "Sem evidência")

LOCKED_MSG = (
    "Não foi possível salvar porque `DADOS.xlsx` está aberto ou "
    "bloqueado por outro processo. Feche a planilha no Excel e tente novamente."
)


class WorkbookError(Exception):
    pass


class LockedError(WorkbookError):
    pass


# ---------------------------------------------------------------- helpers

def slugify(value: str) -> str:
    norm = unicodedata.normalize("NFKD", value or "")
    ascii_only = norm.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "_", ascii_only.lower()).strip("_")
    return slug or "aba"


def sheet_slug(sheet_name: str) -> str:
    return slugify(sheet_name)


def parse_weight(text: Any) -> float:
    if text is None:
        return 0.0
    m = WEIGHT_RE.search(str(text).replace(",", "."))
    if not m:
        return 0.0
    try:
        return float(m.group(1).replace(",", "."))
    except ValueError:
        return 0.0


def extract_code(header: Any) -> str | None:
    if header is None:
        return None
    m = CODE_RE.search(str(header))
    return m.group(0) if m else None


def extract_title(header: Any) -> str:
    if header is None:
        return ""
    text = str(header).strip()
    # remove "M1-11 — " prefixo
    title = re.sub(r"^M\d+-\d+\s*[—–\-]*\s*", "", text).strip()
    return title or text


def entity_key_from(uf: str, label: str) -> str:
    uf = (uf or "").strip().upper()
    lab = (label or "").upper()
    if uf != "ES":
        return uf
    if "SEJUS" in lab:
        return "ES_SEJUS"
    if "POLICIA" in lab or "POLÍCIA" in lab or "POL" in lab:
        # label da Policia Penal contem "POLÍCIA PENAL"; SEJUS ja tratado acima
        return "ES_PP"
    # fallback: nunca mesclar; deriva chave estavel do rotulo
    return "ES_" + slugify(label).upper()[:20]


def get_row4_value(ws, col: int):
    """Resolve valor da linha 4 considerando merges (Item N ...)."""
    for mr in ws.merged_cells.ranges:
        if mr.min_row <= 4 <= mr.max_row and mr.min_col <= col <= mr.max_col:
            return ws.cell(mr.min_row, mr.min_col).value
    return ws.cell(4, col).value


def ensure_dirs() -> None:
    ANEXOS_DIR.mkdir(parents=True, exist_ok=True)
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    EXPORTACOES_DIR.mkdir(parents=True, exist_ok=True)


def ensure_workbook_exists() -> Path:
    if not WORKBOOK_PATH.exists():
        raise WorkbookError(
            "Arquivo DADOS.xlsx não encontrado na raiz do projeto. "
            "Coloque o arquivo DADOS.xlsx na pasta do projeto e reinicie."
        )
    return WORKBOOK_PATH


def open_workbook():
    ensure_workbook_exists()
    try:
        wb = openpyxl.load_workbook(str(WORKBOOK_PATH))
    except Exception as exc:  # noqa: BLE001
        raise WorkbookError(f"Não foi possível abrir DADOS.xlsx: {exc}") from exc
    return wb


# ---------------------------------------------------------------- parsing

def parse_entities(wb) -> list[dict]:
    """Le entidades das linhas 7..34 da aba 01 (A=UF, B=rotulo)."""
    if "01_Institucionalização" not in wb.sheetnames:
        raise WorkbookError("Aba 01_Institucionalização não encontrada.")
    ws = wb["01_Institucionalização"]
    entities: list[dict] = []
    seen: set[str] = set()
    for r in range(DATA_START_ROW, DATA_END_ROW + 1):
        uf = ws.cell(r, 1).value
        label = ws.cell(r, 2).value
        if uf is None and label is None:
            continue
        uf = str(uf).strip() if uf is not None else ""
        label = str(label).strip() if label is not None else uf
        if not uf:
            continue
        key = entity_key_from(uf, label)
        if key in seen:
            raise WorkbookError(f"entity_key duplicada: {key}")
        seen.add(key)
        entities.append({
            "entity_key": key,
            "uf": uf,
            "unidade_label": label,
            "row": r,  # linha nas abas de dimensao
            "resumo_row": RESUMO_START_ROW + (r - DATA_START_ROW),
        })
    # validacao ES duplo
    keys = {e["entity_key"] for e in entities}
    if "ES_PP" not in keys or "ES_SEJUS" not in keys:
        raise WorkbookError("ES deve possuir duas unidades: ES_PP e ES_SEJUS.")
    return entities


def parse_questions(wb, sheet_name: str) -> list[dict]:
    """Mapeia perguntas de uma aba pelo cabecalho da linha 5 (codigos M*-*)."""
    ws = wb[sheet_name]
    max_col = ws.max_column
    is_bonus = sheet_name == "07_Maturidade"
    is_institutional = sheet_name == "01_Institucionalização"
    questions: list[dict] = []
    for c in range(1, max_col + 1):
        header = ws.cell(5, c).value
        code = extract_code(header)
        if not code:
            continue
        # Evita capturar colunas de total que porventura citem codigo (nao ocorre,
        # mas garante que a coluna seja de status: proxima coluna e diagnostico)
        title = extract_title(header)
        item = get_row4_value(ws, c) or ""
        criterio = ws.cell(6, c).value or ""
        if is_bonus:
            weight = 0.0
            m = BONUS_RE.search(str(header))
            if m:
                weight = float(m.group(1).replace(",", "."))
            status_col, resposta_col, fundamento_col, pontos_col = c, c + 1, c + 2, None
            status_options = list(INSTITUTIONAL_STATUSES)
            kind = "bonus"
        elif is_institutional:
            peso_text = ws.cell(5, c + 3).value
            weight = parse_weight(peso_text)
            status_col, resposta_col, fundamento_col, pontos_col = c, c + 1, c + 2, c + 3
            status_options = list(INSTITUTIONAL_STATUSES)
            kind = "institutional"
        else:
            peso_text = ws.cell(5, c + 3).value
            weight = parse_weight(peso_text)
            status_col, resposta_col, fundamento_col, pontos_col = c, c + 1, c + 2, c + 3
            status_options = list(ORDINARY_STATUSES)
            kind = "ordinary"
        occurrence_key = f"{sheet_name}:{code}"
        questions.append({
            "sheet_name": sheet_name,
            "dimension_name": DIMENSION_NAMES.get(sheet_name, sheet_name),
            "item_name": str(item).strip(),
            "question_code": code,
            "question_title": title,
            "occurrence_key": occurrence_key,
            "status_col": status_col,
            "resposta_col": resposta_col,
            "fundamento_col": fundamento_col,
            "pontos_col": pontos_col,
            "weight": float(weight),
            "max_display": f"+{weight:g}" if is_bonus else f"{weight:g} pts",
            "criterio": str(criterio).strip(),
            "status_options": status_options,
            "kind": kind,
        })
    return questions


def parse_all_questions(wb) -> dict[str, list[dict]]:
    result: dict[str, list[dict]] = {}
    for sheet in DIMENSION_SHEETS:
        if sheet not in wb.sheetnames:
            raise WorkbookError(f"Aba {sheet} não encontrada.")
        result[sheet] = parse_questions(wb, sheet)
    return result


def evidences_map(wb) -> dict[tuple[str, str], str]:
    """(entity_key, occurrence_key) -> evidence_text (DB_EVIDENCIAS)."""
    if "DB_EVIDENCIAS" not in wb.sheetnames:
        return {}
    ws = wb["DB_EVIDENCIAS"]
    out: dict[tuple[str, str], str] = {}
    for r in range(2, ws.max_row + 1):
        ek = ws.cell(r, 2).value
        occ = ws.cell(r, 9).value
        txt = ws.cell(r, 10).value
        if ek and occ:
            out[(str(ek), str(occ))] = str(txt) if txt is not None else ""
    return out


def attachments_map(wb, only_active=True) -> dict[tuple[str, str], list[dict]]:
    # DB_ANEXOS: 1 id, 2 entity_key, 3 uf, 4 unidade_label, 5 sheet_name,
    # 6 dimension_name, 7 item_name, 8 question_code, 9 occurrence_key,
    # 10 original_filename, 11 stored_filename, 12 relative_path, 13 mime_type,
    # 14 size_bytes, 15 sha256, 16 uploaded_at, 17 active, 18 notes
    if "DB_ANEXOS" not in wb.sheetnames:
        return {}
    ws = wb["DB_ANEXOS"]
    out: dict[tuple[str, str], list[dict]] = {}
    for r in range(2, ws.max_row + 1):
        ek = ws.cell(r, 2).value
        occ = ws.cell(r, 9).value
        if not ek or not occ:
            continue
        active = ws.cell(r, 17).value
        is_active = str(active).strip().upper() in ("TRUE", "VERDADEIRO", "1", "SIM", "YES", "Y")
        if only_active and not is_active:
            continue
        out.setdefault((str(ek), str(occ)), []).append({
            "id": ws.cell(r, 1).value,
            "entity_key": str(ek),
            "occurrence_key": str(occ),
            "original_filename": ws.cell(r, 10).value or "",
            "stored_filename": ws.cell(r, 11).value or "",
            "relative_path": ws.cell(r, 12).value or "",
            "mime_type": ws.cell(r, 13).value or "",
            "size_bytes": ws.cell(r, 14).value or 0,
            "sha256": ws.cell(r, 15).value or "",
            "uploaded_at": ws.cell(r, 16).value,
            "active": is_active,
            "notes": ws.cell(r, 18).value if ws.max_column >= 18 else "",
            "row": r,
        })
    return out


def score_for(kind: str, status: str | None, weight: float) -> float:
    s = (status or "").strip() or "Sem evidência"
    if kind == "institutional":
        return score_institutional(s)
    if kind == "bonus":
        return score_bonus_item(s, weight)
    return score_ordinary(s, weight)


# ---------------------------------------------------------------- consolidated read

def read_summary() -> tuple[list[dict], dict]:
    """Retorna (rows, cards) calculados em Python (nao depende de cache Excel)."""
    wb = open_workbook()
    try:
        entities = parse_entities(wb)
        all_q = parse_all_questions(wb)
        ev_map = evidences_map(wb)
        _ = ev_map  # evidencias nao afetam pontuacao; mantidas para detalhe
        rows: list[dict] = []
        for ent in entities:
            dim_scores: dict[str, float] = {}
            inst_status = None
            bonus_available = 0.0
            for sheet in DIMENSION_SHEETS:
                ws = wb[sheet]
                total = 0.0
                for q in all_q[sheet]:
                    raw = ws.cell(ent["row"], q["status_col"]).value
                    status = str(raw).strip() if raw is not None and str(raw).strip() else "Sem evidência"
                    if sheet == "01_Institucionalização":
                        inst_status = status
                    sc = score_for(q["kind"], status, q["weight"])
                    total += sc
                    if sheet == "07_Maturidade":
                        bonus_available += sc
                if sheet != "07_Maturidade":
                    dim_scores[sheet] = total
            situacao = situacao_from_status(inst_status)
            base = sum(dim_scores.get(s, 0.0) for s in BASE_WEIGHTS)
            cls = classify(base, bonus_available, situacao, dim_scores)
            rows.append({
                "entity_key": ent["entity_key"],
                "uf": ent["uf"],
                "unidade_label": ent["unidade_label"],
                "dim": {k: round(float(v), 2) for k, v in dim_scores.items()},
                # aliases planos p/ templates (dashboard)
                "inst": round(float(dim_scores.get("01_Institucionalização", 0.0)), 2),
                "aut": round(float(dim_scores.get("02_Autonomia", 0.0)), 2),
                "imp": round(float(dim_scores.get("03_Imparcialidade", 0.0)), 2),
                "aces": round(float(dim_scores.get("04_Acessibilidade", 0.0)), 2),
                "trans": round(float(dim_scores.get("05_Transparência", 0.0)), 2),
                "integ": round(float(dim_scores.get("06_Integração Tec", 0.0)), 2),
                "base_score": None if cls["base_score"] is None else round(cls["base_score"], 2),
                "bonus_available": None if cls["bonus_available"] is None else round(cls["bonus_available"], 2),
                "bonus_applied": None if cls["bonus_applied"] is None else round(cls["bonus_applied"], 2),
                "final_score": None if cls["final_score"] is None else round(cls["final_score"], 2),
                "situacao": situacao,
                "trava": cls["trava"],
                "classification": cls["classification"],
            })
        cards = build_cards(rows)
        return rows, cards
    finally:
        wb.close()


def build_cards(rows: list[dict]) -> dict:
    def count(pred):
        return sum(1 for r in rows if pred(r))

    return {
        "unidades": len(rows),
        "instituidas": count(lambda r: r["situacao"] == "Instituída"),
        "nao_instituidas": count(lambda r: r["situacao"] == "Não instituída"),
        "sem_evidencia": count(lambda r: r["situacao"] == "Sem evidência"),
        "elevada": count(lambda r: r["classification"] == "Instituída — elevada aderência"),
        "satisfatoria": count(lambda r: r["classification"] == "Instituída — aderência satisfatória"),
        "parcial": count(lambda r: r["classification"] == "Instituída — aderência parcial"),
        "baixa_insuficiente": count(
            lambda r: r["classification"]
            in ("Instituída — baixa aderência",
                "Instituída — aderência insuficiente (dimensão essencial zerada)")
        ),
    }


def read_unit_detail(entity_key: str) -> dict:
    wb = open_workbook()
    try:
        entities = parse_entities(wb)
        ent = next((e for e in entities if e["entity_key"] == entity_key), None)
        if ent is None:
            raise WorkbookError(f"Unidade {entity_key} não encontrada.")
        all_q = parse_all_questions(wb)
        ev_map = evidences_map(wb)
        att_map = attachments_map(wb, only_active=True)
        dimensions: list[dict] = []
        dim_scores: dict[str, float] = {}
        inst_status = None
        bonus_available = 0.0
        for sheet in DIMENSION_SHEETS:
            ws = wb[sheet]
            qs: list[dict] = []
            total = 0.0
            for q in all_q[sheet]:
                raw_status = ws.cell(ent["row"], q["status_col"]).value
                status = str(raw_status).strip() if raw_status is not None and str(raw_status).strip() else "Sem evidência"
                resposta = ws.cell(ent["row"], q["resposta_col"]).value
                fundamento = ws.cell(ent["row"], q["fundamento_col"]).value
                if sheet == "01_Institucionalização":
                    inst_status = status
                sc = score_for(q["kind"], status, q["weight"])
                total += sc
                if sheet == "07_Maturidade":
                    bonus_available += sc
                occ = q["occurrence_key"]
                qs.append({
                    **q,
                    "status": status,
                    "resposta": "" if resposta is None else str(resposta),
                    "fundamentacao": "" if fundamento is None else str(fundamento),
                    "score": round(sc, 2),
                    "evidence_text": ev_map.get((entity_key, occ), EVIDENCE_INITIAL_TEXT),
                    "attachments": att_map.get((entity_key, occ), []),
                })
            if sheet != "07_Maturidade":
                dim_scores[sheet] = total
            dimensions.append({
                "sheet_name": sheet,
                "dimension_name": DIMENSION_NAMES.get(sheet, sheet),
                "total": round(total, 2),
                # alias p/ template (unit_detail usa dim.dimension_score)
                "dimension_score": round(total, 2),
                "max": BASE_WEIGHTS.get(sheet, BONUS_MAX if sheet == "07_Maturidade" else 0),
                "questions": qs,
            })
        situacao = situacao_from_status(inst_status)
        base = sum(dim_scores.get(s, 0.0) for s in BASE_WEIGHTS)
        cls = classify(base, bonus_available, situacao, dim_scores)
        result = {
            "situacao": situacao,
            "dim_scores": {k: round(float(v), 2) for k, v in dim_scores.items()},
            "base_score": cls["base_score"],
            "bonus_available": cls["bonus_available"],
            "bonus_applied": cls["bonus_applied"],
            "final_score": cls["final_score"],
            "trava": cls["trava"],
            "classification": cls["classification"],
        }
        return {"entity": ent, "dimensions": dimensions, "result": result}
    finally:
        wb.close()


# ---------------------------------------------------------------- aux sheets / audit

def ensure_aux_sheets(wb, entities: list[dict], all_q: dict[str, list[dict]]) -> bool:
    """Cria DB_EVIDENCIAS/DB_ANEXOS/DB_AUDITORIA se ausentes. Retorna True se alterou."""
    changed = False
    now = datetime.now().isoformat(timespec="seconds")
    if "DB_EVIDENCIAS" not in wb.sheetnames:
        ws = wb.create_sheet("DB_EVIDENCIAS")
        ws.append(DB_EVIDENCIAS_HEADERS)
        nid = 1
        for ent in entities:
            for sheet in DIMENSION_SHEETS:
                for q in all_q[sheet]:
                    ws.append([
                        nid, ent["entity_key"], ent["uf"], ent["unidade_label"],
                        sheet, DIMENSION_NAMES.get(sheet, sheet), q["item_name"],
                        q["question_code"], q["occurrence_key"],
                        EVIDENCE_INITIAL_TEXT, now,
                    ])
                    nid += 1
        try:
            ws.sheet_state = "hidden"
        except Exception:  # noqa: BLE001
            pass
        changed = True
    if "DB_ANEXOS" not in wb.sheetnames:
        ws = wb.create_sheet("DB_ANEXOS")
        ws.append(DB_ANEXOS_HEADERS)
        try:
            ws.sheet_state = "hidden"
        except Exception:  # noqa: BLE001
            pass
        changed = True
    if "DB_AUDITORIA" not in wb.sheetnames:
        ws = wb.create_sheet("DB_AUDITORIA")
        ws.append(DB_AUDITORIA_HEADERS)
        try:
            ws.sheet_state = "hidden"
        except Exception:  # noqa: BLE001
            pass
        changed = True
    return changed


def append_audit(wb, entity_key, sheet_name, question_code, occurrence_key,
                 field, old_value, new_value, action) -> None:
    ws = wb["DB_AUDITORIA"]
    nid = ws.max_row  # header row 1 -> proximo id = max_row (pois id comeca em 1)
    # id = numero de linhas existentes (header conta como 1)
    new_id = ws.max_row  # se so header, max_row=1 -> id=1? ajusta abaixo
    if ws.max_row == 1 and ws.cell(1, 1).value == DB_AUDITORIA_HEADERS[0]:
        # verifica se ha dados
        new_id = 1
    else:
        try:
            last = ws.cell(ws.max_row, 1).value
            new_id = int(last) + 1 if last is not None else ws.max_row
        except (TypeError, ValueError):
            new_id = ws.max_row
    ws.append([
        new_id, datetime.now().isoformat(timespec="seconds"),
        entity_key, sheet_name, question_code, occurrence_key,
        field, "" if old_value is None else str(old_value)[:2000],
        "" if new_value is None else str(new_value)[:2000], action,
    ])
    _ = nid


def upsert_evidence(wb, entity_key, uf, label, q: dict, text: str) -> tuple[str, str]:
    ws = wb["DB_EVIDENCIAS"]
    for r in range(2, ws.max_row + 1):
        if str(ws.cell(r, 2).value) == entity_key and str(ws.cell(r, 9).value) == q["occurrence_key"]:
            old = ws.cell(r, 10).value or ""
            ws.cell(r, 10).value = text
            ws.cell(r, 11).value = datetime.now().isoformat(timespec="seconds")
            return str(old), str(text)
    # nao existia -> cria
    try:
        last = ws.cell(ws.max_row, 1).value
        nid = int(last) + 1 if ws.max_row > 1 and last is not None else 1
    except (TypeError, ValueError):
        nid = ws.max_row
    ws.append([
        nid, entity_key, uf, label, q["sheet_name"],
        DIMENSION_NAMES.get(q["sheet_name"], q["sheet_name"]), q["item_name"],
        q["question_code"], q["occurrence_key"], text,
        datetime.now().isoformat(timespec="seconds"),
    ])
    return "", text


# ---------------------------------------------------------------- safe write

def create_backup() -> Path:
    ensure_dirs()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = BACKUPS_DIR / f"DADOS_{stamp}.xlsx"
    if dest.exists():
        i = 2
        while (BACKUPS_DIR / f"DADOS_{stamp}_{i}.xlsx").exists():
            i += 1
        dest = BACKUPS_DIR / f"DADOS_{stamp}_{i}.xlsx"
    import shutil
    shutil.copy2(str(WORKBOOK_PATH), str(dest))
    return dest


def save_atomic(wb) -> None:
    tmp = WORKBOOK_PATH.parent / "DADOS_tmp_validacao.xlsx"
    try:
        wb.save(str(tmp))
    except PermissionError as exc:
        raise LockedError(LOCKED_MSG) from exc
    except OSError as exc:
        # OneDrive/Excel bloqueio costuma virar PermissionError; trata igual
        if "Permission" in str(type(exc).__name__) or "being used" in str(exc):
            raise LockedError(LOCKED_MSG) from exc
        raise WorkbookError(f"Falha ao salvar temporário: {exc}") from exc
    # reabrir para validar que e XLSX legivel
    try:
        check = openpyxl.load_workbook(str(tmp))
        check.close()
    except Exception as exc:  # noqa: BLE001
        try:
            tmp.unlink(missing_ok=True)
        except Exception:  # noqa: BLE001
            pass
        raise WorkbookError(f"Arquivo temporário inválido, gravação abortada: {exc}") from exc
    try:
        tmp.replace(WORKBOOK_PATH)
    except PermissionError as exc:
        raise LockedError(LOCKED_MSG) from exc


def _acquire_lock() -> FileLock:
    ensure_dirs()
    return FileLock(str(LOCK_PATH), timeout=10)


def find_question(wb, occurrence_key: str) -> dict:
    if ":" not in occurrence_key:
        raise WorkbookError(f"occurrence_key inválida: {occurrence_key}")
    sheet, code = occurrence_key.split(":", 1)
    if sheet not in DIMENSION_SHEETS:
        raise WorkbookError(f"Aba inválida em occurrence_key: {sheet}")
    for q in parse_questions(wb, sheet):
        if q["question_code"] == code:
            return q
    raise WorkbookError(f"Pergunta {occurrence_key} não encontrada.")


def update_assessment(entity_key: str, occurrence_key: str,
                      status: str | None = None,
                      evidence_text: str | None = None):
    """Atualiza status e/ou evidencia com lock+backup+auditoria. Retorna resumo."""
    lock = _acquire_lock()
    try:
        try:
            lock.acquire()
        except Timeout as exc:
            raise LockedError(LOCKED_MSG) from exc
        try:
            create_backup()
            wb = open_workbook()
            try:
                entities = parse_entities(wb)
                ent = next((e for e in entities if e["entity_key"] == entity_key), None)
                if ent is None:
                    raise WorkbookError(f"Unidade {entity_key} não encontrada.")
                q = find_question(wb, occurrence_key)
                if status is not None:
                    if status not in q["status_options"]:
                        raise WorkbookError(
                            f"Status inválido '{status}'. "
                            f"Esperado um de: {', '.join(q['status_options'])}"
                        )
                ws = wb[q["sheet_name"]]
                old_status = ws.cell(ent["row"], q["status_col"]).value
                old_status_s = str(old_status).strip() if old_status not in (None, "") else "Sem evidência"
                all_q = parse_all_questions(wb)
                ensure_aux_sheets(wb, entities, all_q)
                if status is not None and str(status) != str(old_status_s):
                    ws.cell(ent["row"], q["status_col"]).value = status
                    append_audit(wb, entity_key, q["sheet_name"], q["question_code"],
                                 occurrence_key, "status", old_status_s, status,
                                 "mudanca_status")
                new_evidence = None
                if evidence_text is not None:
                    old_ev, new_evidence = upsert_evidence(
                        wb, entity_key, ent["uf"], ent["unidade_label"], q, evidence_text)
                    if old_ev != evidence_text:
                        append_audit(wb, entity_key, q["sheet_name"], q["question_code"],
                                     occurrence_key, "evidence_text", old_ev, evidence_text,
                                     "alteracao_evidencia")
                save_atomic(wb)
            finally:
                wb.close()
        finally:
            try:
                lock.release()
            except Exception:  # noqa: BLE001
                pass
    except LockedError:
        raise
    except WorkbookError:
        raise
    except PermissionError as exc:
        raise LockedError(LOCKED_MSG) from exc
    # recalcula fora do lock
    detail = read_unit_detail(entity_key)
    # localiza pergunta atualizada
    score = dim_total = None
    for dim in detail["dimensions"]:
        for qq in dim["questions"]:
            if qq["occurrence_key"] == occurrence_key:
                score = qq["score"]
                dim_total = dim["total"]
    r = detail["result"]
    return {
        "ok": True,
        "entity_key": entity_key,
        "occurrence_key": occurrence_key,
        "score": score,
        "dimension_score": dim_total,
        "base_score": r["base_score"],
        "bonus_available": r["bonus_available"],
        "bonus_applied": r["bonus_applied"],
        "final_score": r["final_score"],
        "classification": r["classification"],
    }


def correct_diagnostico(entity_key: str, occurrence_key: str, new_value: str):
    lock = _acquire_lock()
    try:
        try:
            lock.acquire()
        except Timeout as exc:
            raise LockedError(LOCKED_MSG) from exc
        try:
            create_backup()
            wb = open_workbook()
            try:
                entities = parse_entities(wb)
                ent = next((e for e in entities if e["entity_key"] == entity_key), None)
                if ent is None:
                    raise WorkbookError(f"Unidade {entity_key} não encontrada.")
                q = find_question(wb, occurrence_key)
                ws = wb[q["sheet_name"]]
                old = ws.cell(ent["row"], q["resposta_col"]).value or ""
                all_q = parse_all_questions(wb)
                ensure_aux_sheets(wb, entities, all_q)
                ws.cell(ent["row"], q["resposta_col"]).value = new_value
                append_audit(wb, entity_key, q["sheet_name"], q["question_code"],
                             occurrence_key, "resposta_diagnostico", old, new_value,
                             "correcao_resposta_diagnostico")
                save_atomic(wb)
            finally:
                wb.close()
        finally:
            try:
                lock.release()
            except Exception:  # noqa: BLE001
                pass
    except LockedError:
        raise
    except PermissionError as exc:
        raise LockedError(LOCKED_MSG) from exc
    return {"ok": True}


# ---------------------------------------------------------------- startup validation

def validate_startup() -> list[str]:
    """Retorna lista de erros (vazia = ok). Nao lanca, para exibir em pagina de erro."""
    errors: list[str] = []
    try:
        ensure_workbook_exists()
    except WorkbookError as exc:
        return [str(exc)]
    try:
        wb = open_workbook()
    except WorkbookError as exc:
        return [str(exc)]
    try:
        for s in EXPECTED_SHEETS:
            if s not in wb.sheetnames:
                errors.append(f"Aba ausente: {s}")
        if errors:
            return errors
        entities = parse_entities(wb)
        if len(entities) != 28:
            errors.append(f"Esperadas 28 unidades de avaliação, encontradas {len(entities)}.")
        all_q = parse_all_questions(wb)
        # pesos conferidos contra 00_Metodologia
        try:
            ws0 = wb["00_Metodologia"]
            for r in range(5, 11):
                dim_label = str(ws0.cell(r, 1).value or "")
                peso = str(ws0.cell(r, 2).value or "").strip()
                for sheet, expected in BASE_WEIGHTS.items():
                    short = sheet.split("_", 1)[1][:4].lower() if "_" in sheet else sheet.lower()
                    if dim_label.lower().startswith(sheet[:2]) and short in dim_label.lower().replace("ç", "c").replace("ã", "a"):
                        if peso != str(expected):
                            errors.append(
                                f"Divergência de peso em 00_Metodologia linha {r}: "
                                f"{dim_label} = {peso}, esperado {expected}."
                            )
        except Exception as exc:  # noqa: BLE001
            errors.append(f"Falha ao conferir 00_Metodologia: {exc}")
        total_w = sum(BASE_WEIGHTS.values())
        if total_w != 100:
            errors.append(f"Soma dos pesos base = {total_w}, esperado 100.")
        bonus_sum = sum(q["weight"] for q in all_q.get("07_Maturidade", []))
        if abs(bonus_sum - BONUS_MAX) > 1e-6:
            errors.append(f"Soma dos bônus = {bonus_sum}, esperado {BONUS_MAX}.")
        if not all_q.get("01_Institucionalização"):
            errors.append("Nenhuma pergunta mapeada em 01_Institucionalização.")
        # caminhos de anexos dentro de ANEXOS
        if "DB_ANEXOS" in wb.sheetnames:
            ws = wb["DB_ANEXOS"]
            for r in range(2, ws.max_row + 1):
                rel = ws.cell(r, 12).value
                if rel and (".." in str(rel) or str(rel).startswith(("/", "\\"))):
                    errors.append(f"DB_ANEXOS linha {r}: caminho fora de ANEXOS: {rel}")
                    break
    except WorkbookError as exc:
        errors.append(str(exc))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"Erro inesperado na validação: {exc}")
    finally:
        try:
            wb.close()
        except Exception:  # noqa: BLE001
            pass
    return errors
