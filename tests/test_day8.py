"""Focused regression tests for the Day 8 agent workflow."""

import unittest
from unittest.mock import patch

from app.agent_loop import run_agent
from app.graph import run_graph
from app.tools import margin_money_subsidy_calculator


class CalculatorTests(unittest.TestCase):
    def test_rates_are_loaded_from_scheme_record(self) -> None:
        result = margin_money_subsidy_calculator(
            1_000_000, "manufacturing", "general", "rural", "PMEGP"
        )
        self.assertEqual(result["source_record_id"], "scheme-pmegp")
        self.assertEqual(result["subsidy_amount"], 250_000.0)
        self.assertEqual(result["own_contribution"], 100_000.0)
        self.assertEqual(result["bank_loan_amount"], 650_000.0)

    def test_service_cap_is_enforced(self) -> None:
        with self.assertRaisesRegex(ValueError, "cannot exceed"):
            margin_money_subsidy_calculator(
                2_000_001, "service", "general", "urban", "CMEGP"
            )


class AgentTests(unittest.TestCase):
    def test_agent_calls_calculator_when_arguments_are_provided(self) -> None:
        result = run_agent(
            "Calculate my PMEGP support",
            {
                "project_cost": 500_000,
                "activity_type": "service",
                "category": "women",
                "rural_urban": "urban",
                "scheme": "PMEGP",
            },
        )
        self.assertEqual(result["mode"], "calculator")
        self.assertIn("subsidy_amount", result["calculation"])

    @patch("app.graph.run_agent")
    def test_graph_requires_approval_only_for_calculator(self, mocked_agent) -> None:
        mocked_agent.return_value = {
            "mode": "rag",
            "answer": "grounded",
            "confidence": "high",
            "follow_up": "none",
            "citations": [],
        }
        result = run_graph("What is PMEGP?", None, False, "test-rag")
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["answer"]["mode"], "rag")

        pending = run_graph(
            "Calculate support",
            {
                "project_cost": 500_000,
                "activity_type": "service",
                "category": "general",
                "rural_urban": "urban",
                "scheme": "CMEGP",
            },
            False,
            "test-approval",
        )
        self.assertEqual(pending["status"], "approval_required")
        self.assertNotIn("calculation", pending["answer"])


if __name__ == "__main__":
    unittest.main()
