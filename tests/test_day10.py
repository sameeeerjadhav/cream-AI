"""Unit tests for UdyamSathi Streamlit UI logic (scheme_fit, calculations, feedback)."""

import json
from pathlib import Path

from ui.app import FEEDBACK_PATH, margin_calc, save_feedback, scheme_fit


def test_ui_scheme_fit_minor_rejected() -> None:
    fit = scheme_fit(17, "General", "Rural", "Manufacturing", 1_000_000)
    assert fit["PMEGP"]["qualifies"] is False
    assert fit["CMEGP"]["qualifies"] is False
    assert any("18 years" in r for r in fit["PMEGP"]["reasons"])
    assert any("18 years" in r for r in fit["CMEGP"]["reasons"])


def test_ui_scheme_fit_manufacturing_qualifies() -> None:
    fit = scheme_fit(25, "General", "Urban", "Manufacturing", 2_000_000)
    assert fit["PMEGP"]["qualifies"] is True
    assert fit["CMEGP"]["qualifies"] is True
    assert fit["PMEGP"]["calculation"] is not None
    assert fit["CMEGP"]["calculation"] is not None


def test_ui_scheme_fit_manufacturing_cap_exceeded() -> None:
    fit = scheme_fit(30, "General", "Rural", "Manufacturing", 5_500_000)
    assert fit["PMEGP"]["qualifies"] is False
    assert fit["CMEGP"]["qualifies"] is False
    assert any("cap" in r.lower() for r in fit["PMEGP"]["reasons"])
    assert any("cap" in r.lower() for r in fit["CMEGP"]["reasons"])


def test_ui_scheme_fit_service_cap_enforced() -> None:
    fit = scheme_fit(28, "Women", "Urban", "Service", 2_200_000)
    assert fit["PMEGP"]["qualifies"] is False
    assert fit["CMEGP"]["qualifies"] is False
    assert any("cap" in r.lower() for r in fit["PMEGP"]["reasons"])
    assert fit["PMEGP"]["calculation"] is None


def test_ui_scheme_fit_cmegp_general_overage() -> None:
    fit = scheme_fit(47, "General", "Rural", "Service", 1_000_000)
    assert fit["PMEGP"]["qualifies"] is True
    assert fit["CMEGP"]["qualifies"] is False
    assert any("age" in r.lower() for r in fit["CMEGP"]["reasons"])
    assert fit["CMEGP"]["calculation"] is None


def test_ui_scheme_fit_cmegp_special_age_relaxed() -> None:
    fit = scheme_fit(48, "Women", "Rural", "Manufacturing", 1_000_000)
    assert fit["PMEGP"]["qualifies"] is True
    assert fit["CMEGP"]["qualifies"] is True
    assert fit["CMEGP"]["calculation"] is not None
    assert fit["PMEGP"]["calculation"] is not None


def test_ui_margin_calc_general_urban() -> None:
    calc = margin_calc(1_000_000, "manufacturing", "general", "urban", "PMEGP")
    assert calc is not None
    assert calc["subsidy_amount"] == 150_000.0  # 15%
    assert calc["own_contribution"] == 100_000.0  # 10%
    assert calc["bank_loan_amount"] == 750_000.0


def test_ui_margin_calc_general_rural() -> None:
    calc = margin_calc(1_000_000, "manufacturing", "general", "rural", "PMEGP")
    assert calc is not None
    assert calc["subsidy_amount"] == 250_000.0  # 25%
    assert calc["own_contribution"] == 100_000.0  # 10%
    assert calc["bank_loan_amount"] == 650_000.0


def test_ui_margin_calc_special_urban() -> None:
    calc = margin_calc(1_000_000, "service", "special", "urban", "CMEGP")
    assert calc is not None
    assert calc["subsidy_amount"] == 250_000.0  # 25%
    assert calc["own_contribution"] == 50_000.0  # 5%
    assert calc["bank_loan_amount"] == 700_000.0


def test_ui_margin_calc_special_rural() -> None:
    calc = margin_calc(1_000_000, "service", "special", "rural", "CMEGP")
    assert calc is not None
    assert calc["subsidy_amount"] == 350_000.0  # 35%
    assert calc["own_contribution"] == 50_000.0  # 5%
    assert calc["bank_loan_amount"] == 600_000.0


def test_ui_margin_calc_zero_or_negative() -> None:
    assert margin_calc(0, "manufacturing", "general", "rural", "PMEGP") is None
    assert margin_calc(-100, "service", "general", "urban", "PMEGP") is None


def test_ui_margin_calc_cap_exceeded_returns_none() -> None:
    assert margin_calc(2_100_000, "service", "general", "urban", "PMEGP") is None
    assert margin_calc(5_500_000, "manufacturing", "general", "rural", "CMEGP") is None


def test_ui_save_feedback_records_to_jsonl() -> None:
    q = "What is the CMEGP limit?"
    a = "Rs 50 Lakh for manufacturing."
    save_feedback(q, a, "thumbs_up")
    assert Path(FEEDBACK_PATH).exists()
    lines = Path(FEEDBACK_PATH).read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) > 0
    last_record = json.loads(lines[-1])
    assert last_record["question"] == q
    assert last_record["answer"] == a
    assert last_record["rating"] == "thumbs_up"


def test_ui_financial_ratio_consistency() -> None:
    calc = margin_calc(1_500_000, "manufacturing", "general", "rural", "PMEGP")
    assert calc is not None
    total = calc["subsidy_amount"] + calc["own_contribution"] + calc["bank_loan_amount"]
    assert total == 1_500_000.0
    assert calc["subsidy_amount"] > 0
    assert calc["own_contribution"] > 0
    assert calc["bank_loan_amount"] > 0


def test_ui_all_special_subcategories_classified() -> None:
    categories = ["SC", "ST", "OBC", "Women", "Minorities", "Ex-servicemen", "Differently abled"]
    for cat in categories:
        fit = scheme_fit(28, cat, "Rural", "Manufacturing", 1_000_000)
        assert fit["PMEGP"]["qualifies"] is True
        calc = fit["PMEGP"]["calculation"]
        assert calc is not None
        assert calc["subsidy_rate"] == 0.35  # Special rural gets 35%
        assert calc["own_contribution_rate"] == 0.05  # Special gets 5%
