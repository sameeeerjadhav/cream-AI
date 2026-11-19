"""Unit tests for Day 2 records module and CLI helpers."""

from app.cli import _render_ascii_table, _render_summary
from app.records import count_by, get_by_id, load_records, search


def test_load_records_returns_all_20() -> None:
    records = load_records()
    assert isinstance(records, list)
    assert len(records) == 20


def test_records_schema_completeness() -> None:
    required_keys = {
        "scheme_name",
        "max_project_cost",
        "subsidy_general",
        "subsidy_special",
        "own_contribution",
        "eligibility",
        "id",
        "category",
    }
    records = load_records()
    for r in records:
        assert required_keys.issubset(r.keys())


def test_records_categories_distribution() -> None:
    records = load_records()
    counts = count_by(records, "category")
    assert counts.get("scheme") == 10
    assert counts.get("msme-limit-2025") == 3
    assert counts.get("pmegp-sub-rule") == 7


def test_records_get_by_id_existing() -> None:
    records = load_records()
    pmegp = get_by_id(records, "scheme-pmegp")
    assert pmegp is not None
    assert "PMEGP" in pmegp["scheme_name"]


def test_records_get_by_id_missing() -> None:
    records = load_records()
    assert get_by_id(records, "non-existent-key-12345") is None


def test_records_search_matching_keyword() -> None:
    records = load_records()
    results = search(records, "manufacturing")
    assert len(results) > 0
    assert any("manufacturing" in str(r).lower() for r in results)


def test_records_search_empty_returns_empty() -> None:
    records = load_records()
    assert search(records, "") == []
    assert search(records, "   ") == []


def test_records_search_case_insensitive() -> None:
    records = load_records()
    res_lower = search(records, "subsidy")
    res_upper = search(records, "SUBSIDY")
    assert len(res_lower) == len(res_upper)


def test_cli_table_renderer(capsys) -> None:
    records = load_records()[:3]
    _render_ascii_table(records)
    captured = capsys.readouterr()
    assert "Scheme Name" in captured.out
    assert "Total: 3 records" in captured.out


def test_cli_summary_renderer(capsys) -> None:
    records = load_records()
    _render_summary(records)
    captured = capsys.readouterr()
    assert "Total Records Count: 20" in captured.out
    assert "Breakdown by Category" in captured.out
