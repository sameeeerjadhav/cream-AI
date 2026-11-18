"""Deterministic tools for UdyamSathi financial estimates."""

import re
from typing import Any

from data.sample_records import RECORDS


def _scheme_rules(scheme_key: str) -> dict[str, Any]:
    record = next(
        (item for item in RECORDS if item.get("id") == f"scheme-{scheme_key}"),
        None,
    )
    if record is None:
        raise ValueError(f"No stored record found for {scheme_key.upper()}")

    max_cost = re.findall(
        r"Rs\s*(\d+)\s*lakh\s*(manufacturing|service)",
        record["max_project_cost"],
        re.IGNORECASE,
    )
    if len(max_cost) != 2:
        raise ValueError(f"Invalid project-cost limits stored for {scheme_key.upper()}")
    caps = {
        activity.casefold(): float(amount) * 100_000 for amount, activity in max_cost
    }

    general = re.search(
        r"(\d+)%\s*urban,\s*(\d+)%\s*rural", record["subsidy_general"], re.IGNORECASE
    )
    special = re.search(
        r"(\d+)%\s*urban,\s*(\d+)%\s*rural", record["subsidy_special"], re.IGNORECASE
    )
    own = re.search(
        r"(\d+)%\s*general;\s*(\d+)%\s*special",
        record["own_contribution"],
        re.IGNORECASE,
    )
    if not general or not special or not own:
        raise ValueError(f"Invalid subsidy rates stored for {scheme_key.upper()}")
    return {
        "name": record["scheme_name"],
        "record_id": record["id"],
        "caps": caps,
        "subsidy_rates": {
            "general": {
                "urban": int(general.group(1)) / 100,
                "rural": int(general.group(2)) / 100,
            },
            "special": {
                "urban": int(special.group(1)) / 100,
                "rural": int(special.group(2)) / 100,
            },
        },
        "own_rates": {
            "general": int(own.group(1)) / 100,
            "special": int(own.group(2)) / 100,
        },
    }


def _normalize(value: str, field: str, aliases: dict[str, str]) -> str:
    normalized = value.strip().casefold().replace("-", "_").replace(" ", "_")
    if normalized not in aliases:
        allowed = ", ".join(sorted(set(aliases.values())))
        raise ValueError(f"{field} must be one of: {allowed}")
    return aliases[normalized]


def margin_money_subsidy_calculator(
    project_cost: float,
    activity_type: str,
    category: str,
    rural_urban: str,
    scheme: str,
) -> dict[str, Any]:
    """Calculate subsidy, applicant contribution, and bank finance.

    Rates and caps are the PMEGP/CMEGP values captured in the project records:
    general 15% urban/25% rural, special 25% urban/35% rural, with
    manufacturing capped at Rs 50 lakh and service capped at Rs 20 lakh.
    """
    if project_cost <= 0:
        raise ValueError("project_cost must be greater than zero")
    activity = _normalize(
        activity_type,
        "activity_type",
        {"manufacturing": "manufacturing", "service": "service"},
    )
    applicant_category = _normalize(
        category,
        "category",
        {
            "general": "general",
            "special": "special",
            "sc": "special",
            "st": "special",
            "obc": "special",
            "women": "special",
            "woman": "special",
            "minority": "special",
            "ex_servicemen": "special",
            "differently_abled": "special",
        },
    )
    location = _normalize(
        rural_urban,
        "rural_urban",
        {"rural": "rural", "urban": "urban"},
    )
    scheme_key = _normalize(
        scheme,
        "scheme",
        {"pmegp": "pmegp", "cmegp": "cmegp"},
    )
    rules = _scheme_rules(scheme_key)
    cap = rules["caps"][activity]
    if project_cost > cap:
        raise ValueError(
            f"{rules['name']} {activity} project cost cannot exceed Rs {cap:,.0f}"
        )

    subsidy_rate = rules["subsidy_rates"][applicant_category][location]
    own_rate = rules["own_rates"][applicant_category]
    subsidy = round(project_cost * subsidy_rate, 2)
    own_contribution = round(project_cost * own_rate, 2)
    bank_loan = round(project_cost - subsidy - own_contribution, 2)
    return {
        "scheme": rules["name"],
        "source_record_id": rules["record_id"],
        "project_cost": round(project_cost, 2),
        "activity_type": activity,
        "category": applicant_category,
        "rural_urban": location,
        "project_cost_cap": cap,
        "subsidy_rate": subsidy_rate,
        "own_contribution_rate": own_rate,
        "subsidy_amount": subsidy,
        "own_contribution": own_contribution,
        "bank_loan_amount": bank_loan,
        "note": "Estimate only; final sanction and eligibility are decided by the implementing authority and lender.",
    }
