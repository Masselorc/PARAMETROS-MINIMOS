"""Caminhos e constantes globais do sistema.

Todos os caminhos sao relativos a raiz do projeto (pasta que contem DADOS.xlsx).
Nunca gravar caminho absoluto de OneDrive ou nome de usuario no codigo.
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

WORKBOOK_FILENAME = "DADOS.xlsx"
WORKBOOK_PATH = BASE_DIR / WORKBOOK_FILENAME
LOCK_PATH = BASE_DIR / ".dados.lock"

ANEXOS_DIR = BASE_DIR / "ANEXOS"
BACKUPS_DIR = BASE_DIR / "BACKUPS"
EXPORTACOES_DIR = BASE_DIR / "EXPORTACOES"

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".xls", ".csv", ".png", ".jpg", ".jpeg", ".txt"}
MAX_UPLOAD_BYTES = 25 * 1024 * 1024  # 25 MB

EVIDENCE_INITIAL_TEXT = "Doc. SEI 37070578"

# Abas principais esperadas (nomes exatos da planilha real)
EXPECTED_SHEETS = [
    "00_Metodologia",
    "01_Institucionalização",
    "02_Autonomia",
    "03_Imparcialidade",
    "04_Acessibilidade",
    "05_Transparência",
    "06_Integração Tec",
    "07_Maturidade",
    "08_Resumo",
]

DIMENSION_SHEETS = [
    "01_Institucionalização",
    "02_Autonomia",
    "03_Imparcialidade",
    "04_Acessibilidade",
    "05_Transparência",
    "06_Integração Tec",
    "07_Maturidade",
]

# Nome amigavel por aba
DIMENSION_NAMES = {
    "01_Institucionalização": "Institucionalização",
    "02_Autonomia": "Autonomia",
    "03_Imparcialidade": "Imparcialidade",
    "04_Acessibilidade": "Acessibilidade",
    "05_Transparência": "Transparência",
    "06_Integração Tec": "Integração tecnológica",
    "07_Maturidade": "Maturidade / bônus",
}

# Pesos maximos por dimensao (conferidos contra 00_Metodologia)
BASE_WEIGHTS = {
    "01_Institucionalização": 15,
    "02_Autonomia": 15,
    "03_Imparcialidade": 15,
    "04_Acessibilidade": 15,
    "05_Transparência": 15,
    "06_Integração Tec": 25,
}

BONUS_MAX = 10

DB_EVIDENCIAS_HEADERS = [
    "id", "entity_key", "uf", "unidade_label", "sheet_name", "dimension_name",
    "item_name", "question_code", "occurrence_key", "evidence_text", "updated_at",
]
DB_ANEXOS_HEADERS = [
    "id", "entity_key", "uf", "unidade_label", "sheet_name", "dimension_name",
    "item_name", "question_code", "occurrence_key", "original_filename",
    "stored_filename", "relative_path", "mime_type", "size_bytes", "sha256",
    "uploaded_at", "active", "notes",
]
DB_AUDITORIA_HEADERS = [
    "id", "timestamp", "entity_key", "sheet_name", "question_code",
    "occurrence_key", "field", "old_value", "new_value", "action",
]
