"""Aplicacao FastAPI — Parametros Minimos das Ouvidorias de Servicos Penais.

Execucao local:
    uvicorn app:app --host 127.0.0.1 --port 8000
"""
from pathlib import Path
from urllib.parse import unquote

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.attachments import get_attachment, store_attachment, unlink_attachment
from src.config import BASE_DIR, BASE_WEIGHTS, DIMENSION_MINIMUMS, DIMENSION_NAMES
from src.reports import (
    generate_general_pdf,
    generate_general_xlsx,
    generate_unit_pdf,
    generate_unit_xlsx,
)
from src.schemas import AssessmentPatch, CorrectDiagnostico
from src.workbook_service import (
    LOCKED_MSG,
    LockedError,
    WorkbookError,
    correct_diagnostico,
    ensure_dirs,
    open_workbook,
    parse_entities,
    read_all_unit_details,
    read_methodology_matrix,
    read_summary,
    read_unit_detail,
    sort_pt_filter,
    summarize_uf_indicator,
    update_assessment,
    validate_startup,
)

app = FastAPI(title="Parâmetros Mínimos — ONASP", version="0.1.0")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
templates.env.filters["sort_pt"] = sort_pt_filter
static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

STARTUP_ERRORS: list[str] = []


@app.on_event("startup")
def _startup() -> None:
    ensure_dirs()
    global STARTUP_ERRORS
    STARTUP_ERRORS = validate_startup()


@app.middleware("http")
async def _ensure_dirs_middleware(request: Request, call_next):
    # Garante validacao mesmo se o servidor rodar sem eventos startup
    # (ex.: TestClient sem context manager).
    global STARTUP_ERRORS
    if not STARTUP_ERRORS:
        try:
            ensure_dirs()
            STARTUP_ERRORS = validate_startup()
        except Exception:  # noqa: BLE001
            pass
    return await call_next(request)


def _guard_startup():
    global STARTUP_ERRORS
    if not STARTUP_ERRORS:
        return
    if any(LOCKED_MSG in error for error in STARTUP_ERRORS):
        STARTUP_ERRORS = validate_startup()
        if not STARTUP_ERRORS:
            return
        if any(LOCKED_MSG in error for error in STARTUP_ERRORS):
            raise HTTPException(status_code=409, detail="; ".join(STARTUP_ERRORS))
    raise HTTPException(status_code=500, detail="; ".join(STARTUP_ERRORS))


def _filters(request: Request) -> dict:
    q = (request.query_params.get("q") or "").strip().lower()
    situacoes = [s for s in request.query_params.getlist("situacao") if s]
    classificacoes = [c for c in request.query_params.getlist("classificacao") if c]
    unidades = [u for u in request.query_params.getlist("unidade") if u]
    return {
        "q": request.query_params.get("q") or "",
        "situacoes": situacoes,
        "classificacoes": classificacoes,
        "unidades": unidades,
        "situacao": situacoes[0] if len(situacoes) == 1 else (request.query_params.get("situacao") or ""),
        "classificacao": classificacoes[0] if len(classificacoes) == 1 else (request.query_params.get("classificacao") or ""),
        "nota_min": request.query_params.get("nota_min") or "",
        "nota_max": request.query_params.get("nota_max") or "",
        "_q": q,
    }


CLASSIFICATION_ALIASES = {
    "seguindo": "Instituída — seguindo os parâmetros mínimos",
    "seguindo_minimos": "Instituída — seguindo os parâmetros mínimos",
    "abaixo_dimensao": "Instituída — abaixo do mínimo em dimensão essencial",
    "abaixo_minimo_dimensao": "Instituída — abaixo do mínimo em dimensão essencial",
    "global_insuficiente": "Instituída — aderência global insuficiente",
    "aderencia_global_insuficiente": "Instituída — aderência global insuficiente",
    "nao_instituida": "Não instituída",
    "não_instituída": "Não instituída",
    "nao_comprovada": "Instituição não comprovada",
    "instituicao_nao_comprovada": "Instituição não comprovada",
    # aliases legados (matriz anterior as novas faixas)
    "elevada": "Instituída — seguindo os parâmetros mínimos",
    "satisfatoria": "Instituída — seguindo os parâmetros mínimos",
    "satisfatória": "Instituída — seguindo os parâmetros mínimos",
    "parcial": "Instituída — aderência global insuficiente",
    "baixa": "Instituída — aderência global insuficiente",
    "insuficiente": "Instituída — abaixo do mínimo em dimensão essencial",
    "sem_evidencia": "Instituição não comprovada",
    "sem_evidência": "Instituição não comprovada",
}


def _apply_filters(rows: list[dict], f: dict) -> list[dict]:
    out = []
    try:
        nmin = float(f["nota_min"]) if f["nota_min"] not in ("", None) else None
    except ValueError:
        nmin = None
    try:
        nmax = float(f["nota_max"]) if f["nota_max"] not in ("", None) else None
    except ValueError:
        nmax = None

    wanted_situacoes = set(f.get("situacoes") or ([f["situacao"]] if f.get("situacao") else []))
    raw_classifs = f.get("classificacoes") or ([f["classificacao"]] if f.get("classificacao") else [])
    wanted_classificacoes = {CLASSIFICATION_ALIASES.get(c, c) for c in raw_classifs if c}
    wanted_unidades = set(f.get("unidades") or [])

    for r in rows:
        if wanted_situacoes and r["situacao"] not in wanted_situacoes:
            continue
        if wanted_classificacoes and r["classification"] not in wanted_classificacoes:
            continue
        if wanted_unidades and r.get("entity_key") not in wanted_unidades and r.get("uf") not in wanted_unidades:
            continue
        if nmin is not None and (r["final_score"] is None or r["final_score"] < nmin):
            continue
        if nmax is not None and (r["final_score"] is None or r["final_score"] > nmax):
            continue
        if f["_q"] and f["_q"] not in f"{r['uf']} {r['unidade_label']}".lower():
            continue
        out.append(r)
    out.sort(key=lambda r: (r["final_score"] is None, -(r["final_score"] or 0)))
    return out


# ---------------------------------------------------------------- paginas

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    _guard_startup()
    rows, cards = read_summary()
    f = _filters(request)
    unit_options = sort_pt_filter(rows, "unidade_label")
    return templates.TemplateResponse(request, "dashboard.html", {
        "rows": _apply_filters(rows, f),
        "cards": cards, "filters": f,
        "unit_options": unit_options,
    })


@app.get("/unidades", response_class=HTMLResponse)
def units(request: Request):
    _guard_startup()
    rows, _ = read_summary()
    f = _filters(request)
    unit_options = sort_pt_filter(rows, "unidade_label")
    return templates.TemplateResponse(request, "units.html", {
        "rows": _apply_filters(rows, f), "filters": f,
        "unit_options": unit_options,
    })


@app.get("/unidades/{entity_key}", response_class=HTMLResponse)
def unit_detail(entity_key: str, request: Request):
    _guard_startup()
    try:
        detail = read_unit_detail(entity_key)
    except WorkbookError as exc:
        return templates.TemplateResponse(request, "error.html", {
            "message": str(exc), "detail": "",
        }, status_code=404)
    return templates.TemplateResponse(request, "unit_detail.html", {
        "entity": detail["entity"],
        "dimensions": detail["dimensions"], "result": detail["result"],
    })


@app.get("/relatorios", response_class=HTMLResponse)
def reports_page(request: Request):
    _guard_startup()
    rows, cards = read_summary()
    all_details = read_all_unit_details()
    unit_options = sort_pt_filter(rows, "unidade_label")
    units = sort_pt_filter([all_details[r["entity_key"]]["entity"] for r in rows if r["entity_key"] in all_details], "unidade_label")
    selected_key = request.query_params.get("unidade") or (units[0]["entity_key"] if units else "AC")
    return templates.TemplateResponse(request, "reports.html", {
        "units": units,
        "unit_options": unit_options,
        "rows": rows,
        "cards": cards,
        "all_details": all_details,
        "selected_key": selected_key,
        "base_weights": BASE_WEIGHTS,
        "dimension_minimums": DIMENSION_MINIMUMS,
    })


@app.get("/metodologia", response_class=HTMLResponse)
def methodology(request: Request):
    _guard_startup()
    return templates.TemplateResponse(request, "methodology.html", {
        "methodology_dimensions": read_methodology_matrix(),
    })


# ---------------------------------------------------------------- API leitura

@app.get("/api/health")
def api_health():
    if STARTUP_ERRORS:
        return {"ok": False, "errors": STARTUP_ERRORS}
    return {"ok": True}


@app.get("/api/resumo")
def api_resumo():
    _guard_startup()
    rows, cards = read_summary()
    return {"cards": cards, "rows": rows, "uf_indicator": summarize_uf_indicator(rows)}


@app.get("/api/indicador-pena-justa")
def api_indicador_pena_justa():
    """Indicador 2.4.2.1.2.1 por UF (ES aparece com 2 unidades, sem consolidar)."""
    _guard_startup()
    rows, _ = read_summary()
    return summarize_uf_indicator(rows)


@app.get("/api/unidades")
def api_units():
    _guard_startup()
    rows, _ = read_summary()
    return {"unidades": rows}


@app.get("/api/unidades/{entity_key}")
def api_unit(entity_key: str):
    _guard_startup()
    try:
        detail = read_unit_detail(entity_key)
    except WorkbookError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return detail


@app.get("/api/unidades/{entity_key}/avaliacoes")
def api_unit_avaliacoes(entity_key: str):
    _guard_startup()
    try:
        detail = read_unit_detail(entity_key)
    except WorkbookError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    out = []
    for dim in detail["dimensions"]:
        for q in dim["questions"]:
            out.append({k: q[k] for k in (
                "occurrence_key", "question_code", "question_title", "status",
                "score", "evidence_text") if k in q})
    return {"entity_key": entity_key, "avaliacoes": out}


@app.get("/api/unidades/{entity_key}/avaliacoes/{occurrence_key}/anexos")
def api_list_anexos(entity_key: str, occurrence_key: str):
    _guard_startup()
    occurrence_key = unquote(occurrence_key)
    try:
        detail = read_unit_detail(entity_key)
    except WorkbookError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    for dim in detail["dimensions"]:
        for q in dim["questions"]:
            if q["occurrence_key"] == occurrence_key:
                return {"anexos": q["attachments"]}
    raise HTTPException(status_code=404, detail="Pergunta não encontrada.")


# ---------------------------------------------------------------- API alteracoes

@app.patch("/api/unidades/{entity_key}/avaliacoes/{occurrence_key}")
def api_patch_assessment(entity_key: str, occurrence_key: str, body: AssessmentPatch):
    _guard_startup()
    occurrence_key = unquote(occurrence_key)
    status = body.status
    evidence = body.evidence_text
    if evidence is None and body.observation not in (None, ""):
        evidence = body.observation
    if status is None and evidence is None:
        raise HTTPException(status_code=422, detail="Informe status e/ou evidence_text.")
    try:
        return update_assessment(entity_key, occurrence_key, status=status,
                                 evidence_text=evidence)
    except LockedError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except WorkbookError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/unidades/{entity_key}/avaliacoes/{occurrence_key}/corrigir-resposta")
async def api_correct(entity_key: str, occurrence_key: str, request: Request):
    """Aceita JSON {"new_value": ...} (fetch) ou form (textarea name=resposta)."""
    _guard_startup()
    occurrence_key = unquote(occurrence_key)
    new_value = None
    ctype = (request.headers.get("content-type") or "").lower()
    if "application/json" in ctype:
        try:
            payload = await request.json()
        except Exception:  # noqa: BLE001
            payload = {}
        new_value = (payload or {}).get("new_value", (payload or {}).get("resposta"))
    else:
        try:
            form = await request.form()
            new_value = form.get("new_value", form.get("resposta"))
        except Exception:  # noqa: BLE001
            new_value = None
    if new_value is None or str(new_value).strip() == "":
        # form HTML puro deve redirecionar de volta ao detalhe
        if "application/json" not in ctype and "text/html" in (request.headers.get("accept") or ""):
            raise HTTPException(status_code=422, detail="Informe o novo texto da resposta.")
        raise HTTPException(status_code=422, detail="Informe new_value.")
    try:
        result = correct_diagnostico(entity_key, occurrence_key, str(new_value))
    except LockedError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except WorkbookError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    # Se veio de form HTML, redireciona de volta ao detalhe (PRG)
    if "application/json" not in ctype:
        accept = request.headers.get("accept") or ""
        if "text/html" in accept or "multipart/form-data" in ctype or "urlencoded" in ctype:
            from fastapi.responses import RedirectResponse
            return RedirectResponse(url=f"/unidades/{entity_key}", status_code=303)
    return result


@app.post("/api/unidades/{entity_key}/avaliacoes/{occurrence_key}/anexos")
async def api_upload(entity_key: str, occurrence_key: str, request: Request,
                     file: UploadFile = File(...), notes: str = Form(default="")):
    _guard_startup()
    occurrence_key = unquote(occurrence_key)
    data = await file.read()
    try:
        result = store_attachment(entity_key, occurrence_key,
                                  file.filename or "arquivo", data, notes or "")
    except LockedError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except WorkbookError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    # form HTML puro -> PRG de volta ao detalhe
    accept = request.headers.get("accept") or ""
    if "text/html" in accept:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=f"/unidades/{entity_key}", status_code=303)
    return result


@app.post("/api/anexos/{attachment_id}/desvincular")
async def api_unlink(attachment_id: str, request: Request):
    _guard_startup()
    try:
        result = unlink_attachment(attachment_id)
    except LockedError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except WorkbookError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    accept = request.headers.get("accept") or ""
    if "text/html" in accept:
        from fastapi.responses import RedirectResponse
        referer = request.headers.get("referer") or "/"
        return RedirectResponse(url=referer, status_code=303)
    return result


@app.get("/anexos/{attachment_id}/abrir")
def anexo_abrir(attachment_id: str):
    _guard_startup()
    try:
        meta = get_attachment(attachment_id)
    except WorkbookError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FileResponse(str(meta["path"]), media_type=meta["mime_type"],
                        filename=meta["original_filename"])


@app.get("/anexos/{attachment_id}/baixar")
def anexo_baixar(attachment_id: str):
    _guard_startup()
    try:
        meta = get_attachment(attachment_id)
    except WorkbookError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FileResponse(str(meta["path"]), media_type=meta["mime_type"],
                        filename=meta["original_filename"],
                        content_disposition_type="attachment")


# ---------------------------------------------------------------- relatorios download

@app.get("/api/relatorios/geral.pdf")
def rel_geral_pdf(request: Request):
    _guard_startup()
    rows, cards = read_summary()
    rows = _apply_filters(rows, _filters(request))
    path = generate_general_pdf(rows, cards)
    return FileResponse(str(path), media_type="application/pdf",
                        filename=path.name)


@app.get("/api/relatorios/geral.xlsx")
def rel_geral_xlsx(request: Request):
    _guard_startup()
    rows, cards = read_summary()
    rows = _apply_filters(rows, _filters(request))
    path = generate_general_xlsx(rows, cards)
    return FileResponse(
        str(path),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=path.name)


@app.get("/api/relatorios/{entity_key}.pdf")
def rel_unit_pdf(entity_key: str):
    _guard_startup()
    try:
        path = generate_unit_pdf(entity_key)
    except WorkbookError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FileResponse(str(path), media_type="application/pdf", filename=path.name)


@app.get("/api/relatorios/{entity_key}.xlsx")
def rel_unit_xlsx(entity_key: str):
    _guard_startup()
    try:
        path = generate_unit_xlsx(entity_key)
    except WorkbookError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FileResponse(
        str(path),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=path.name)


@app.exception_handler(WorkbookError)
async def _wb_handler(request: Request, exc: WorkbookError):
    return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})
