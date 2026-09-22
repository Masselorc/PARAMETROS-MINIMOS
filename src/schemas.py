"""Schemas da API (contratos de entrada/saida)."""
from typing import Optional

from pydantic import BaseModel, Field


class AssessmentPatch(BaseModel):
    status: Optional[str] = Field(default=None, description="Atende/Parcial/... ou Sim/Não/... conforme pergunta")
    evidence_text: Optional[str] = Field(default=None, description="Texto livre de evidencia/observacao")
    observation: Optional[str] = Field(default=None, description="Alias compativel com a especificacao")


class CorrectDiagnostico(BaseModel):
    new_value: str = Field(description="Novo texto da resposta do diagnostico")


class UnlinkResponse(BaseModel):
    ok: bool = True
