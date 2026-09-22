"""Pontuacao: Atende=100%, Parcial=50%; pisos 50% + base>=70; 5 classificações."""
from src.config import DIMENSION_MINIMUMS, GLOBAL_BASE_MINIMUM
from src.scoring import (
    classify,
    dimensions_below_minimum,
    meets_minimum_parameters,
    score_bonus_item,
    score_institutional,
    score_ordinary,
    situacao_from_status,
    validate_weights,
)


def _full_dims():
    return {
        "02_Autonomia": 15, "03_Imparcialidade": 15, "04_Acessibilidade": 15,
        "05_Transparência": 15, "06_Integração Tec": 25,
    }


def _min_dims():
    return {
        "02_Autonomia": 7.5, "03_Imparcialidade": 7.5, "04_Acessibilidade": 7.5,
        "05_Transparência": 7.5, "06_Integração Tec": 12.5,
    }


def test_weights_sum():
    validate_weights()


def test_ordinary():
    assert score_ordinary("Atende", 3) == 3
    assert score_ordinary("Parcial", 3) == 1.5
    assert score_ordinary("Não atende", 3) == 0
    assert score_ordinary("Sem evidência", 3) == 0
    assert score_ordinary("Atende", 5) == 5
    assert score_ordinary("Parcial", 5) == 2.5
    assert score_ordinary("Atende", 8) == 8
    assert score_ordinary("Parcial", 8) == 4
    assert score_ordinary("Atende", 7) == 7
    assert score_ordinary("Parcial", 7) == 3.5


def test_institutional():
    assert score_institutional("Sim") == 15
    assert score_institutional("Não") == 0
    assert score_institutional("Sem evidência") == 0


def test_bonus_limited_to_100():
    r = classify(96, 8, "Instituída", _full_dims())
    assert r["bonus_applied"] == 4
    assert r["final_score"] == 100
    assert r["final_score"] <= 100


def test_bonus_nao_decide_parametros_minimos():
    # base 68 + bônus 7 => final 75, mas segue global insuficiente
    r = classify(68, 7, "Instituída", _full_dims())
    assert r["final_score"] == 75
    assert r["meets_minimum_parameters"] is False
    assert r["classification"] == "Instituída — aderência global insuficiente"


def test_bonus_max():
    assert score_bonus_item("Sim", 3) == 3
    assert score_bonus_item("Não", 3) == 0
    assert score_bonus_item("Sem evidência", 2) == 0


def test_nao_instituida_sem_classificacao_normal():
    r = classify(0, 0, "Não instituída", {})
    assert r["classification"] == "Não instituída"
    assert r["final_score"] is None
    # bonus nao transforma em instituida
    r2 = classify(0, 10, "Não instituída", {})
    assert r2["classification"] == "Não instituída"


def test_trava_dimensao_zerada():
    dims = dict(_min_dims())
    dims["03_Imparcialidade"] = 0
    r = classify(62.5, 5, "Instituída", dims)
    assert r["dimensions_below_minimum"] == ["03_Imparcialidade"]
    assert r["meets_minimum_parameters"] is False
    assert r["classification"] == "Instituída — abaixo do mínimo em dimensão essencial"


def test_cinco_casos_classificacao():
    assert classify(0, 0, "Não instituída", {})["classification"] == "Não instituída"
    assert classify(0, 0, "Instituição não comprovada", {})["classification"] == "Instituição não comprovada"
    low = dict(_min_dims()); low["02_Autonomia"] = 7.4
    assert classify(70, 0, "Instituída", low)["classification"] == "Instituída — abaixo do mínimo em dimensão essencial"
    assert classify(69.9, 10, "Instituída", _min_dims())["classification"] == "Instituída — aderência global insuficiente"
    r = classify(70, 5, "Instituída", _min_dims())
    assert r["classification"] == "Instituída — seguindo os parâmetros mínimos"
    assert r["meets_minimum_parameters"] is True


def test_pisos_sao_metade_do_maximo():
    assert DIMENSION_MINIMUMS == {
        "02_Autonomia": 7.5, "03_Imparcialidade": 7.5, "04_Acessibilidade": 7.5,
        "05_Transparência": 7.5, "06_Integração Tec": 12.5,
    }
    assert GLOBAL_BASE_MINIMUM == 70
    assert dimensions_below_minimum(_min_dims()) == []
    low = dict(_min_dims()); low["06_Integração Tec"] = 12.4
    assert dimensions_below_minimum(low) == ["06_Integração Tec"]
    assert meets_minimum_parameters("Instituída", 70, _min_dims()) is True
    assert meets_minimum_parameters("Instituída", 70, low) is False
    assert meets_minimum_parameters("Instituída", 69.9, _min_dims()) is False


def test_faixas():
    def cls(base, dims=None):
        return classify(base, 0, "Instituída", dims or _min_dims())["classification"]
    assert cls(69.9) == "Instituída — aderência global insuficiente"
    assert cls(70) == "Instituída — seguindo os parâmetros mínimos"
    assert cls(100, _full_dims()) == "Instituída — seguindo os parâmetros mínimos"


def test_situacao():
    assert situacao_from_status("Sim") == "Instituída"
    assert situacao_from_status("Não") == "Não instituída"
    assert situacao_from_status("Sem evidência") == "Instituição não comprovada"
    assert situacao_from_status("") == "Instituição não comprovada"


def test_sem_institucionalizacao_nao_recebe_classificacao_ordinaria():
    result = classify(100, 10, "Não instituída", {})
    assert result["classification"] == "Não instituída"
    assert result["base_score"] is None
    assert result["bonus_applied"] is None
    assert result["final_score"] is None
    assert result["meets_minimum_parameters"] is False


def test_sem_evidencia_nao_recebe_classificacao_ordinaria():
    result = classify(100, 10, "Instituição não comprovada", {})
    assert result["classification"] == "Instituição não comprovada"
    assert result["final_score"] is None
    assert result["meets_minimum_parameters"] is False
