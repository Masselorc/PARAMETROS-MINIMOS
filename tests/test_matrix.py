"""A matriz corrente define codigos exclusivos e pesos oficiais por dimensao."""
from collections import Counter, defaultdict

import openpyxl

from src import config
from src.reports import generate_unit_xlsx
from src.workbook_service import (
    open_workbook,
    parse_all_questions,
    parse_entities,
    read_unit_detail,
    validate_question_uniqueness,
    validate_startup,
)


def _matrix_questions():
    wb = open_workbook()
    try:
        return parse_all_questions(wb)
    finally:
        wb.close()


def test_official_base_and_bonus_totals():
    config_base_total = sum(config.BASE_WEIGHTS.values())
    bonus_total = sum(config.EXPECTED_QUESTION_WEIGHTS["07_Maturidade"].values())
    assert config_base_total == 100
    assert bonus_total == config.BONUS_MAX == 10
    assert sum(
        sum(config.EXPECTED_QUESTION_WEIGHTS[s].values())
        for s in config.BASE_WEIGHTS
    ) == 100


def test_current_matrix_codes_and_weights_match_official_distribution():
    questions = _matrix_questions()
    actual = {
        sheet: {q["question_code"]: q["weight"] for q in items}
        for sheet, items in questions.items()
    }
    assert actual == {
        sheet: {code: float(weight) for code, weight in weights.items()}
        for sheet, weights in config.EXPECTED_QUESTION_WEIGHTS.items()
    }


def test_no_question_code_is_duplicated_in_base_or_bonus():
    questions = _matrix_questions()
    assert validate_question_uniqueness(questions) == []
    codes = [q["question_code"] for items in questions.values() for q in items]
    assert len(codes) == 30
    assert len(codes) == len(set(codes))


def test_duplicate_error_identifies_code_and_dimensions():
    errors = validate_question_uniqueness({
        "02_Autonomia": [{"question_code": "M4-67"}],
        "06_Integração Tec": [{"question_code": "M4-67"}],
    })
    assert errors == [
        "Pergunta duplicada na matriz: M4-67 aparece em mais de uma dimensão "
        "(Autonomia técnica e funcional; Integração tecnológica)."
    ]


def test_codes_moved_to_their_single_official_dimensions():
    questions = _matrix_questions()
    locations = defaultdict(list)
    for sheet, items in questions.items():
        for question in items:
            locations[question["question_code"]].append(sheet)
    assert locations["M1-12"] == ["02_Autonomia"]
    assert locations["M4-67"] == ["02_Autonomia"]
    assert locations["M4-66"] == ["06_Integração Tec"]
    assert locations["M2-37"] == ["06_Integração Tec"]
    assert locations["M2-45"] == ["06_Integração Tec"]


def test_startup_accepts_new_matrix_and_keeps_two_es_entities():
    assert validate_startup() == []
    wb = open_workbook()
    try:
        entities = parse_entities(wb)
    finally:
        wb.close()
    assert len(entities) == 28
    es = {e["entity_key"]: e for e in entities if e["uf"] == "ES"}
    assert set(es) == {"ES_PP", "ES_SEJUS"}
    assert es["ES_PP"]["row"] != es["ES_SEJUS"]["row"]


def test_new_classification_cases_use_only_base_score():
    from src.scoring import classify

    minimums = {
        "02_Autonomia": 7.5, "03_Imparcialidade": 7.5, "04_Acessibilidade": 7.5,
        "05_Transparência": 7.5, "06_Integração Tec": 12.5,
    }
    full = {
        "02_Autonomia": 15, "03_Imparcialidade": 15, "04_Acessibilidade": 15,
        "05_Transparência": 15, "06_Integração Tec": 25,
    }
    assert classify(0, 0, "Não instituída", {})["classification"] == "Não instituída"
    assert classify(0, 0, "Instituição não comprovada", {})["classification"] == "Instituição não comprovada"
    low = dict(minimums); low["04_Acessibilidade"] = 7.4
    below = classify(85, 5, "Instituída", low)
    assert below["classification"] == "Instituída — abaixo do mínimo em dimensão essencial"
    assert below["meets_minimum_parameters"] is False
    # O bônus aplicado participa do mínimo global pela nota final.
    following = classify(68, 7, "Instituída", full)
    assert following["final_score"] == 75
    assert following["meets_minimum_parameters"] is True
    assert following["classification"] == "Instituída — seguindo os parâmetros mínimos"
    insufficient = classify(60, 5, "Instituída", full)
    assert insufficient["final_score"] == 65
    assert insufficient["classification"] == "Instituída — aderência global insuficiente"
    ok = classify(70, 4, "Instituída", minimums)
    assert ok["classification"] == "Instituída — seguindo os parâmetros mínimos"
    assert ok["meets_minimum_parameters"] is True


def test_individual_xlsx_lists_only_questions_in_current_matrix(tmp_path, monkeypatch):
    import src.reports as reports

    monkeypatch.setattr(reports, "EXPORTACOES_DIR", tmp_path / "EXPORTACOES")
    path = generate_unit_xlsx("AC")
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        ws = wb["Avaliação detalhada"]
        rows = list(ws.iter_rows(min_row=2, values_only=True))
        reported = [(row[0], row[1]) for row in rows]
    finally:
        wb.close()

    detail = read_unit_detail("AC")
    expected = [
        (dim["dimension_name"], question["question_code"])
        for dim in detail["dimensions"]
        for question in dim["questions"]
    ]
    assert reported == expected
    counts = Counter(code for _, code in reported)
    assert len(reported) == 30
    assert all(count == 1 for count in counts.values())
