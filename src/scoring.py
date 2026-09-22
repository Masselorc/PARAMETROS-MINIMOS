"""Motor de pontuacao em Python (fonte explicita e testavel).

Nao depende do cache de formulas do Excel: o frontend e os relatorios
usam este motor; o Excel permanece coerente via formulas ja existentes.
"""
from .config import BASE_WEIGHTS, BONUS_MAX

ORDINARY_VALUES = ("Atende", "Parcial", "Não atende", "Sem evidência")
INSTITUTIONAL_VALUES = ("Sim", "Não", "Sem evidência")
BONUS_VALUES = ("Sim", "Não", "Sem evidência")

# Dimensoes sujeitas a trava quando totalmente zeradas
ESSENTIAL_DIMENSIONS = [
    "02_Autonomia",
    "03_Imparcialidade",
    "04_Acessibilidade",
    "05_Transparência",
    "06_Integração Tec",
]


def score_ordinary(status, weight: float) -> float:
    """Atende=100%, Parcial=50%, demais=0."""
    if status == "Atende":
        return float(weight)
    if status == "Parcial":
        return float(weight) / 2.0
    return 0.0


def score_institutional(status) -> float:
    """M1-11: Sim=15, demais=0."""
    return 15.0 if status == "Sim" else 0.0


def score_bonus_item(status, bonus_value: float) -> float:
    """Bonus: Sim concede o valor, demais zero."""
    return float(bonus_value) if status == "Sim" else 0.0


def situacao_from_status(status) -> str:
    if status == "Sim":
        return "Instituída"
    if status == "Não":
        return "Não instituída"
    return "Sem evidência"


def classify(
    base_score: float,
    bonus_available: float,
    situacao: str,
    dim_scores: dict,
) -> dict:
    """Aplica trava, bonus limitado e faixas. Espelha formulas do 08_Resumo."""
    if situacao != "Instituída":
        return {
            "base_score": None,
            "bonus_available": None,
            "bonus_applied": None,
            "final_score": None,
            "trava": False,
            "classification": situacao,  # "Não instituída" ou "Sem evidência"
        }
    trava = any(float(dim_scores.get(d, 0) or 0) == 0 for d in ESSENTIAL_DIMENSIONS)
    bonus_applied = min(float(bonus_available or 0), max(0.0, 100.0 - float(base_score or 0)))
    final_score = min(100.0, float(base_score or 0) + bonus_applied)
    if trava:
        classification = "Instituída — aderência insuficiente (dimensão essencial zerada)"
    elif final_score < 50:
        classification = "Instituída — baixa aderência"
    elif final_score < 70:
        classification = "Instituída — aderência parcial"
    elif final_score < 90:
        classification = "Instituída — aderência satisfatória"
    else:
        classification = "Instituída — elevada aderência"
    return {
        "base_score": float(base_score or 0),
        "bonus_available": float(bonus_available or 0),
        "bonus_applied": float(bonus_applied),
        "final_score": float(final_score),
        "trava": bool(trava),
        "classification": classification,
    }


def validate_weights() -> None:
    total = sum(BASE_WEIGHTS.values())
    assert total == 100, f"BASE_WEIGHTS soma {total}, esperado 100"
    assert BONUS_MAX == 10, "BONUS_MAX deve ser 10"
