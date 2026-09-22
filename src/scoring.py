"""Motor de pontuacao em Python (fonte explicita e testavel).

Nao depende do cache de formulas do Excel: o frontend e os relatorios
usam este motor; o Excel permanece coerente via formulas ja existentes.
"""
from .config import (
    BASE_WEIGHTS,
    BONUS_MAX,
    DIMENSION_MINIMUMS,
    DIMENSION_SHEETS,
    EXPECTED_QUESTION_WEIGHTS,
    GLOBAL_BASE_MINIMUM,
)

ORDINARY_VALUES = ("Atende", "Parcial", "Não atende", "Sem evidência")
INSTITUTIONAL_VALUES = ("Sim", "Não", "Sem evidência")
BONUS_VALUES = ("Sim", "Não", "Sem evidência")

# Dimensões essenciais sujeitas ao piso de 50% para "seguir os parâmetros"
ESSENTIAL_DIMENSIONS = list(DIMENSION_MINIMUMS)


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
    return "Instituição não comprovada"


def dimensions_below_minimum(dim_scores: dict) -> list[str]:
    """Sheets essenciais abaixo de 50% do máximo (ordem de ESSENTIAL_DIMENSIONS)."""
    return [
        sheet for sheet in ESSENTIAL_DIMENSIONS
        if float(dim_scores.get(sheet, 0) or 0) < DIMENSION_MINIMUMS[sheet]
    ]


def meets_minimum_parameters(situacao: str, base_score: float, dim_scores: dict) -> bool:
    """True somente para instituída com nota-base>=70 e pisos dimensionais."""
    if situacao != "Instituída":
        return False
    if float(base_score or 0) < GLOBAL_BASE_MINIMUM:
        return False
    return not dimensions_below_minimum(dim_scores)


def classify(
    base_score: float,
    bonus_available: float,
    situacao: str,
    dim_scores: dict,
) -> dict:
    """Pisos de 50% por dimensão essencial + nota-base>=70. Bonus não decide."""
    if situacao != "Instituída":
        return {
            "base_score": None,
            "bonus_available": None,
            "bonus_applied": None,
            "final_score": None,
            "meets_minimum_parameters": False,
            "dimensions_below_minimum": [],
            "classification": situacao,  # "Não instituída" ou "Instituição não comprovada"
        }
    base = float(base_score or 0)
    below = dimensions_below_minimum(dim_scores)
    bonus_applied = min(float(bonus_available or 0), max(0.0, 100.0 - base))
    final_score = min(100.0, base + bonus_applied)
    meets = not below and base >= GLOBAL_BASE_MINIMUM
    if below:
        classification = "Instituída — abaixo do mínimo em dimensão essencial"
    elif base < GLOBAL_BASE_MINIMUM:
        classification = "Instituída — aderência global insuficiente"
    else:
        classification = "Instituída — seguindo os parâmetros mínimos"
    return {
        "base_score": base,
        "bonus_available": float(bonus_available or 0),
        "bonus_applied": float(bonus_applied),
        "final_score": float(final_score),
        "meets_minimum_parameters": bool(meets),
        "dimensions_below_minimum": below,
        "classification": classification,
    }


def validate_weights() -> None:
    total = sum(BASE_WEIGHTS.values())
    assert total == 100, f"BASE_WEIGHTS soma {total}, esperado 100"
    assert BONUS_MAX == 10, "BONUS_MAX deve ser 10"
    assert set(EXPECTED_QUESTION_WEIGHTS) == set(DIMENSION_SHEETS), (
        "Distribuição esperada não cobre exatamente as sete abas de avaliação"
    )
    base_questions = sum(
        sum(EXPECTED_QUESTION_WEIGHTS[sheet].values())
        for sheet in BASE_WEIGHTS
    )
    assert base_questions == total, (
        f"Pesos das perguntas-base somam {base_questions}, esperado {total}"
    )
    bonus_questions = sum(EXPECTED_QUESTION_WEIGHTS["07_Maturidade"].values())
    assert bonus_questions == BONUS_MAX, (
        f"Pesos de bônus somam {bonus_questions}, esperado {BONUS_MAX}"
    )
    assert set(DIMENSION_MINIMUMS) == set(ESSENTIAL_DIMENSIONS), (
        "Pisos mínimos devem cobrir exatamente as dimensões essenciais"
    )
    for sheet, minimum in DIMENSION_MINIMUMS.items():
        assert abs(minimum - BASE_WEIGHTS[sheet] / 2.0) < 1e-6, (
            f"Piso de {sheet} deve ser 50% do máximo ({BASE_WEIGHTS[sheet]})"
        )
    assert GLOBAL_BASE_MINIMUM == 70, "Nota-base mínima global deve ser 70"
