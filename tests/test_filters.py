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


def test_droplist_alphabetical_sorting_in_all_pages():
    import re
    from src.workbook_service import sort_pt_key

    client = TestClient(app)

    for path in ["/", "/unidades", "/relatorios"]:
        res = client.get(path)
        assert res.status_code == 200
        # Encontra o bloco do filtro de unidade
        match = re.search(r'data-filter-name="unidade".*?<div class="ms-options-list">(.*?)</div>', res.text, re.DOTALL)
        assert match is not None, f"Filtro de unidade não encontrado em {path}"
        options = re.findall(r'<span class="ms-option-label">(.*?)</span>', match.group(1))
        assert len(options) >= 27
        # Verifica se as opções estão em ordem alfabética segundo collation pt-BR
        sorted_options = sorted(options, key=sort_pt_key)
        assert options == sorted_options, f"Opções não estão em ordem alfabética em {path}"

    # Relatório individual unit-select
    res_rep = client.get("/relatorios")
    select_match = re.search(r'<select id="unit-select"[^>]*>(.*?)</select>', res_rep.text, re.DOTALL)
    assert select_match is not None
    select_options = re.findall(r'<option[^>]*>(.*?)</option>', select_match.group(1))
    assert len(select_options) >= 27
    sorted_select = sorted(select_options, key=lambda s: sort_pt_key(s.split("—", 1)[1]))
    assert select_options == sorted_select



