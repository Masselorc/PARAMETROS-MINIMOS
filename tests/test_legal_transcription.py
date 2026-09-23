# -*- coding: utf-8 -*-
"""Testes para transcrição de dispositivos legais e sincronização de evidências."""
import pytest
from pathlib import Path

from src.legal_texts import LEGAL_TEXTS, get_fundamentacao_teor_html, get_fundamentacao_teor_plain
from src.workbook_service import open_workbook, parse_all_questions, read_unit_detail, read_all_unit_details
from src.reports import generate_unit_pdf


def test_legal_texts_all_questions_covered():
    """Valida que todas as 30 perguntas da metodologia possuem transcrição do teor."""
    wb = open_workbook()
    all_q = parse_all_questions(wb)
    wb.close()

    total = 0
    missing = []
    for sheet, qs in all_q.items():
        for q in qs:
            total += 1
            occ = q["occurrence_key"]
            if occ not in LEGAL_TEXTS:
                missing.append(occ)

    assert total == 30, f"Esperava 30 perguntas na planilha, encontrou {total}"
    assert len(missing) == 0, f"Perguntas sem transcrição legal: {missing}"
    assert len(LEGAL_TEXTS) == 30


def test_legal_texts_html_and_plain_output():
    """Valida o funcionamento dos geradores HTML e texto plano."""
    for occ in LEGAL_TEXTS:
        html = get_fundamentacao_teor_html(occ)
        plain = get_fundamentacao_teor_plain(occ)
        assert "<p>" in html, f"HTML para {occ} deve conter tag <p>"
        assert len(plain) > 10, f"Texto plano para {occ} não pode ser vazio"


def test_spreadsheet_evidence_read():
    """Valida que valores preenchidos diretamente na planilha DADOS.xlsx são refletidos."""
    detail = read_unit_detail("SC")
    q1 = detail["dimensions"][0]["questions"][0]
    assert q1["question_code"] == "M1-11"
    # Em DADOS.xlsx, linha 31 de Santa Catarina possui 'Decreto'
    assert q1["evidence_text"] == "Decreto"

    all_details = read_all_unit_details()
    assert all_details["SC"]["dimensions"][0]["questions"][0]["evidence_text"] == "Decreto"


def test_fundamentacao_teor_populated_in_unit_detail():
    """Valida que fundamentacao_teor está preenchida para todas as perguntas da unidade."""
    detail = read_unit_detail("SC")
    for dim in detail["dimensions"]:
        for q in dim["questions"]:
            assert "fundamentacao_teor" in q
            assert len(q["fundamentacao_teor"]) > 0
            assert "<p>" in q["fundamentacao_teor"]

    # Verifica especificamente M1-11
    q1 = detail["dimensions"][0]["questions"][0]
    assert "Art. 6º A criação da Ouvidoria de Serviços Penais" in q1["fundamentacao_teor"]


def test_pdf_generation_includes_legal_transcription(tmp_path):
    """Valida geração do PDF individual com os novos teores legais."""
    pdf_path = generate_unit_pdf("SC")
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 5000
    # Limpa arquivo gerado
    try:
        pdf_path.unlink()
    except Exception:
        pass
