"""Testes de marcação e acessibilidade dos seletores de status na página de detalhe da unidade."""
from starlette.testclient import TestClient

from app import app


def test_unit_detail_status_selects():
    client = TestClient(app)
    # AC possui perguntas com Sim, Não atende, Atende, etc.
    response = client.get("/unidades/AC")
    assert response.status_code == 200
    html = response.text

    assert "data-status-select" in html
    assert "data-status-type=" in html
    assert "onchange=\"if(window.updateStatusSelectColor)window.updateStatusSelectColor(this);\"" in html
    assert "oninput=\"if(window.updateStatusSelectColor)window.updateStatusSelectColor(this);\"" in html

    # Verifica classes semânticas geradas pelo Jinja
    assert "status-good" in html
    assert "status-bad" in html

    # Verifica se a função window.updateStatusSelectColor está no script inline
    assert "window.updateStatusSelectColor = updateStatusSelectColor;" in html
    assert "function getStatusType(val)" in html
