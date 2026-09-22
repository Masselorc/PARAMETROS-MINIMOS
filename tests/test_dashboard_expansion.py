"""Testes da expansão de linha na tabela da Visão Geral (dashboard)."""
from starlette.testclient import TestClient

from app import app


def test_dashboard_renders_row_expansion_structure():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    html = response.text

    # Verifica se os elementos de controle e de detalhe estao presentes
    assert "class=\"row-expand\"" in html
    assert "class=\"row-summary-detail\"" in html
    assert "colspan=\"13\"" in html

    # Contagem de 28 unidades
    assert html.count("class=\"row-expand\"") == 28
    assert html.count("class=\"row-summary-detail\"") == 28
    assert html.count("data-detail-for=") == 28

    # Verifica presenca dos blocos informativos exigidos
    assert "Resumo Diagnóstico Rápido" in html
    assert "Resultado Consolidado" in html
    assert "Nota-Base" in html
    assert "Bônus Aplicado" in html
    assert "Nota Final" in html
    assert "Mínimo Global (70 pts)" in html
    assert "Dimensões e Pisos Regulamentares (IN nº 75/2026)" in html
    assert "1. Institucionalização" in html
    assert "2. Autonomia" in html
    assert "3. Imparcialidade" in html
    assert "4. Acessibilidade" in html
    assert "5. Transparência" in html
    assert "6. Integração Tec" in html
    assert "Diagnóstico Rápido e Motivo da Classificação" in html
    assert "Abrir avaliação completa de" in html


def test_dashboard_expansion_diagnostics_content():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    html = response.text

    # Casos determinísticos avaliados:
    # 1. Unidade seguindo os parâmetros (ex: AC)
    assert "Todas as dimensões essenciais atingem o piso mínimo regulamentar de 50%" in html

    # 2. Unidade com dimensão essencial abaixo do piso (ex: MA tem Transparência abaixo do piso)
    assert "A unidade possui nota-base de" in html
    assert "piso: 7,5" in html
    assert "déficit:" in html
    assert "#dim-4" in html

    # 3. Unidade não instituída (ex: PA)
    assert "A unidade não possui Ouvidoria de Serviços Penais formalmente instituída segundo o critério normativo M1-11." in html
