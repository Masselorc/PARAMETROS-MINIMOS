"""Pontuacao: Atende=100%, Parcial=50%, demais=0; bonus limitado a 100; trava."""
from src.scoring import (
    classify,
    score_bonus_item,
    score_institutional,
    score_ordinary,
    situacao_from_status,
    validate_weights,
)


def test_weights_sum():
    validate_weights()


def test_ordinary():
    assert score_ordinary("Atende", 3) == 3
    assert score_ordinary("Parcial", 3) == 1.5
    assert score_ordinary("Não atende", 3) == 0
    assert score_ordinary("Sem evidência", 3) == 0
    assert score_ordinary("Atende", 5) == 5
    assert score_ordinary("Parcial", 5) == 2.5


def test_institutional():
    assert score_institutional("Sim") == 15
    assert score_institutional("Não") == 0
    assert score_institutional("Sem evidência") == 0


def test_bonus_limited_to_100():
    r = classify(96, 8, "Instituída", {
        "02_Autonomia": 10, "03_Imparcialidade": 10, "04_Acessibilidade": 10,
        "05_Transparência": 10, "06_Integração Tec": 10,
    })
    assert r["bonus_applied"] == 4
    assert r["final_score"] == 100
    assert r["final_score"] <= 100


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
    dims = {
        "02_Autonomia": 12, "03_Imparcialidade": 0, "04_Acessibilidade": 10,
        "05_Transparência": 10, "06_Integração Tec": 10,
    }
    r = classify(42, 5, "Instituída", dims)
    assert r["trava"] is True
    assert r["classification"] == "Instituída — aderência insuficiente (dimensão essencial zerada)"


def test_faixas():
    def cls(base):
        dims = {d: 5 for d in (
            "02_Autonomia", "03_Imparcialidade", "04_Acessibilidade",
            "05_Transparência", "06_Integração Tec")}
        return classify(base, 0, "Instituída", dims)["classification"]
    assert cls(30) == "Instituída — baixa aderência"
    assert cls(60) == "Instituída — aderência parcial"
    assert cls(80) == "Instituída — aderência satisfatória"
    assert cls(95) == "Instituída — elevada aderência"


def test_situacao():
    assert situacao_from_status("Sim") == "Instituída"
    assert situacao_from_status("Não") == "Não instituída"
    assert situacao_from_status("Sem evidência") == "Sem evidência"
