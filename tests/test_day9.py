"""Comprehensive Day 9 Agent, Tools, and LangGraph Workflow Regression Tests."""

import unittest
from unittest.mock import patch

from app.agent_loop import run_agent
from app.graph import run_graph
from app.tools import (
    eligibility_criteria_checker,
    margin_money_subsidy_calculator,
    msme_classification_checker,
)


class Day9ToolTests(unittest.TestCase):
    def test_pmegp_general_rural_calculation(self) -> None:
        res = margin_money_subsidy_calculator(
            1_000_000, "manufacturing", "general", "rural", "PMEGP"
        )
        self.assertEqual(res["subsidy_amount"], 250_000.0)
        self.assertEqual(res["own_contribution"], 100_000.0)
        self.assertEqual(res["bank_loan_amount"], 650_000.0)
        self.assertEqual(res["source_record_id"], "scheme-pmegp")

    def test_pmegp_special_urban_calculation(self) -> None:
        res = margin_money_subsidy_calculator(
            1_000_000, "manufacturing", "women", "urban", "PMEGP"
        )
        self.assertEqual(res["subsidy_amount"], 250_000.0)
        self.assertEqual(res["own_contribution"], 50_000.0)
        self.assertEqual(res["bank_loan_amount"], 700_000.0)

    def test_pmegp_special_rural_max_subsidy(self) -> None:
        res = margin_money_subsidy_calculator(
            2_000_000, "manufacturing", "sc", "rural", "PMEGP"
        )
        self.assertEqual(res["subsidy_amount"], 700_000.0)  # 35% of 20L
        self.assertEqual(res["own_contribution"], 100_000.0)  # 5% of 20L
        self.assertEqual(res["bank_loan_amount"], 1_200_000.0)

    def test_service_cap_enforcement_cmegp(self) -> None:
        with self.assertRaisesRegex(ValueError, "cannot exceed"):
            margin_money_subsidy_calculator(
                2_500_000, "service", "general", "urban", "CMEGP"
            )

    def test_zero_or_negative_project_cost_raises_error(self) -> None:
        with self.assertRaises(ValueError):
            margin_money_subsidy_calculator(
                0, "service", "general", "urban", "PMEGP"
            )

    def test_msme_classification_micro(self) -> None:
        res = msme_classification_checker(8_000_000, 40_000_000)
        self.assertEqual(res["classification"], "Micro")
        self.assertEqual(res["source_record_id"], "msme-micro-2025")

    def test_msme_classification_small(self) -> None:
        res = msme_classification_checker(50_000_000, 200_000_000)
        self.assertEqual(res["classification"], "Small")
        self.assertEqual(res["source_record_id"], "msme-small-2025")

    def test_msme_classification_medium(self) -> None:
        res = msme_classification_checker(300_000_000, 1_500_000_000)
        self.assertEqual(res["classification"], "Medium")
        self.assertEqual(res["source_record_id"], "msme-medium-2025")

    def test_msme_classification_beyond_limits(self) -> None:
        res = msme_classification_checker(600_000_000, 3_000_000_000)
        self.assertEqual(res["classification"], "Large / Beyond MSME")

    def test_eligibility_criteria_age_and_cap_checks(self) -> None:
        # Minor
        minor = eligibility_criteria_checker(16, "general", 500_000, "service", "pmegp")
        self.assertFalse(minor["is_eligible"])
        self.assertIn("at least 18", minor["reasons"][0])

        # Over-age for CMEGP general
        overage = eligibility_criteria_checker(48, "general", 500_000, "service", "cmegp")
        self.assertFalse(overage["is_eligible"])

        # Eligible CMEGP special category (up to 50 years)
        special_ok = eligibility_criteria_checker(48, "women", 500_000, "service", "cmegp")
        self.assertTrue(special_ok["is_eligible"])


class Day9GraphAgentTests(unittest.TestCase):
    def test_agent_routes_to_calculator(self) -> None:
        res = run_agent(
            "Calculate support",
            {
                "project_cost": 500_000,
                "activity_type": "service",
                "category": "general",
                "rural_urban": "rural",
                "scheme": "PMEGP",
            },
        )
        self.assertEqual(res["mode"], "calculator")
        self.assertIn("subsidy_amount", res["calculation"])

    @patch("app.graph.run_agent")
    def test_langgraph_requires_approval_gate(self, mocked_agent) -> None:
        mocked_agent.return_value = {
            "mode": "rag",
            "answer": "PMEGP information",
            "confidence": "high",
            "follow_up": "none",
            "citations": [],
        }
        # Non-calculation questions bypass approval
        rag_res = run_graph("What is PMEGP?", None, False, "th-rag")
        self.assertEqual(rag_res["status"], "completed")

        # Calculator request without approval pauses with approval_required
        calc_payload = {
            "project_cost": 1_000_000,
            "activity_type": "manufacturing",
            "category": "general",
            "rural_urban": "rural",
            "scheme": "PMEGP",
        }
        pending = run_graph("Calculate", calc_payload, False, "th-calc")
        self.assertEqual(pending["status"], "approval_required")

        # Approved request proceeds to completion
        completed = run_graph("Calculate", calc_payload, True, "th-calc")
        self.assertEqual(completed["status"], "completed")


if __name__ == "__main__":
    unittest.main()
