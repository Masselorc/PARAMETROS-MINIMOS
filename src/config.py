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
    "02_Autonomia": "Autonomia técnica e funcional",
    "03_Imparcialidade": "Imparcialidade, sigilo e proteção",
    "04_Acessibilidade": "Acessibilidade e atendimento humanizado",
    "05_Transparência": "Transparência e publicidade",
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

# Pisos mínimos por dimensão essencial (50% do máximo) e nota-base global
# mínima para "seguir os parâmetros mínimos". A Institucionalização é
# binária (15 = instituída) e não usa piso percentual.
DIMENSION_MINIMUMS = {
    "02_Autonomia": 7.5,
    "03_Imparcialidade": 7.5,
    "04_Acessibilidade": 7.5,
    "05_Transparência": 7.5,
    "06_Integração Tec": 12.5,
}

GLOBAL_BASE_MINIMUM = 70

# Distribuicao oficial usada para validar os codigos e os pesos lidos dos
# cabecalhos do DADOS.xlsx. Isto nao mapeia coordenadas de coluna.
EXPECTED_QUESTION_WEIGHTS = {
    "01_Institucionalização": {"M1-11": 15},
    "02_Autonomia": {
        "M3-56": 3,
        "M3-57": 3,
        "M1-12": 3,
        "M4-67": 3,
        "M4-68": 3,
    },
    "03_Imparcialidade": {"M4-69": 8, "M3-63": 7},
    "04_Acessibilidade": {
        "M2-41": 2,
        "M2-43": 2,
        "M2-47": 2,
        "M2-16": 3,
        "M1-13": 3,
        "M4-64": 3,
    },
    "05_Transparência": {"M2-35": 5, "M4-71": 10},
    "06_Integração Tec": {
        "M2-45": 5,
        "M4-66": 5,
        "M2-37": 5,
        "M2-17": 4,
        "M2-19": 2,
        "M2-21": 2,
        "M2-27": 2,
    },
    "07_Maturidade": {
        "M2-46": 3,
        "M0-08": 1,
        "M3-60": 1,
        "M3-58": 1,
        "M2-50": 1,
        "M2-49": 1,
        "M2-36": 2,
    },
}

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
