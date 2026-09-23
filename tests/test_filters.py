"""Testes para filtros multi-select, faixa de nota e ordenação padrão."""
from starlette.testclient import TestClient

from app import app
from src.workbook_service import read_summary


def test_default_sorting_by_final_score_descending():
    rows, _ = read_summary()
    # Verifica que as linhas com nota final estão em ordem decrescente
    scored_rows = [r for r in rows if r["final_score"] is not None]
    scores = [r["final_score"] for r in scored_rows]
    assert scores == sorted(scores, reverse=True)
    # Linhas sem nota aparecem ao final
    unscored_rows = [r for r in rows if r["final_score"] is None]
    assert len(rows) == len(scored_rows) + len(unscored_rows)


def test_filter_bar_rendered_in_all_pages():
    client = TestClient(app)

    # 1. Dashboard
    res_dash = client.get("/")
    assert res_dash.status_code == 200
    assert 'class="filters-bar"' in res_dash.text
    assert 'class="range-input range-min"' in res_dash.text
    assert 'class="range-input range-max"' in res_dash.text
    assert 'data-filter-name="unidade"' in res_dash.text

    # 2. Unidades
    res_units = client.get("/unidades")
    assert res_units.status_code == 200
    assert 'class="filters-bar"' in res_units.text
    assert 'class="range-input range-min"' in res_units.text
    assert 'class="range-input range-max"' in res_units.text
    assert 'data-filter-name="unidade"' in res_units.text

    # 3. Relatórios
    res_rep = client.get("/relatorios")
    assert res_rep.status_code == 200
    assert 'id="general-report-filters"' in res_rep.text
    assert 'class="range-input range-min"' in res_rep.text
    assert 'class="range-input range-max"' in res_rep.text
    assert 'data-filter-name="unidade"' in res_rep.text
    # Logo oficial do governo federal no cabeçalho do relatório
    assert "logo_senappen_mjsp_gov_horizontal.png" in res_rep.text


def test_multi_select_and_range_filtering_query():
    client = TestClient(app)

    # Filtra por múltiplas situações
    res = client.get("/?situacao=Instituída&situacao=Não instituída")
    assert res.status_code == 200

    # Filtra por faixa de nota
    res_range = client.get("/?nota_min=70&nota_max=90")
    assert res_range.status_code == 200
