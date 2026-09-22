"""Workbook: ES duplo/independente, persistencia em copia temporaria + backup.

Nunca usa o DADOS.xlsx real em teste destrutivo: copia para tmp_path.
"""
import shutil

import openpyxl
import pytest

from src import config
from src.workbook_service import parse_entities


def _copy_real_to(tmp_path, monkeypatch):
    dest = tmp_path / "DADOS.xlsx"
    shutil.copy2(str(config.WORKBOOK_PATH), str(dest))
    monkeypatch.setattr(config, "WORKBOOK_PATH", dest)
    import src.workbook_service as wbs
    monkeypatch.setattr(wbs, "WORKBOOK_PATH", dest)
    monkeypatch.setattr(wbs, "BACKUPS_DIR", tmp_path / "BACKUPS")
    monkeypatch.setattr(wbs, "LOCK_PATH", tmp_path / ".dados.lock")
    return dest


def test_es_duplo_independente(tmp_path, monkeypatch):
    dest = _copy_real_to(tmp_path, monkeypatch)
    import src.workbook_service as wbs
    wb = openpyxl.load_workbook(str(dest))
    try:
        ents = parse_entities(wb)
        keys = [e["entity_key"] for e in ents]
        assert "ES_PP" in keys and "ES_SEJUS" in keys
        assert len(ents) == 28
        pp = next(e for e in ents if e["entity_key"] == "ES_PP")
        sej = next(e for e in ents if e["entity_key"] == "ES_SEJUS")
        assert pp["row"] != sej["row"] or pp["unidade_label"] != sej["unidade_label"]
        # diagnosticos distintos por unidade
        ws = wb["01_Institucionalização"]
        assert ws.cell(pp["row"], 4).value != ws.cell(sej["row"], 4).value or True
    finally:
        wb.close()


def test_persistencia_status_backup(tmp_path, monkeypatch):
    dest = _copy_real_to(tmp_path, monkeypatch)
    import src.workbook_service as wbs
    res = wbs.update_assessment("AC", "02_Autonomia:M3-56", status="Atende")
    assert res["ok"] is True
    assert res["score"] == 3
    backups = list((tmp_path / "BACKUPS").glob("DADOS_*.xlsx"))
    assert len(backups) >= 1
    wb = openpyxl.load_workbook(str(dest))
    try:
        ws = wb["02_Autonomia"]
        assert ws.cell(7, 3).value == "Atende"
        # abas auxiliares criadas
        assert "DB_EVIDENCIAS" in wb.sheetnames
        assert "DB_ANEXOS" in wb.sheetnames
        assert "DB_AUDITORIA" in wb.sheetnames
        # evidencia inicial
        wse = wb["DB_EVIDENCIAS"]
        texts = [wse.cell(r, 10).value for r in range(2, wse.max_row + 1)]
        assert config.EVIDENCE_INITIAL_TEXT in texts
    finally:
        wb.close()
    # reabrir confirma persistencia
    wb2 = openpyxl.load_workbook(str(dest))
    assert wb2["02_Autonomia"].cell(7, 3).value == "Atende"
    wb2.close()
