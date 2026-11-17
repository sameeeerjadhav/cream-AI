"""Hand-written agent orchestration for UdyamSathi."""

from typing import Any

from app.rag import answer_question
from app.tools import margin_money_subsidy_calculator


def run_agent(
    question: str,
    calculator_args: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Route a question to RAG or explicitly requested calculator tooling."""
    if calculator_args is None:
        result = answer_question(question)
        return {
            "mode": "rag",
            "answer": result.answer,
            "confidence": result.confidence,
            "follow_up": result.follow_up,
            "citations": result.citations,
            "steps": ["retrieved_chunks", "generated_grounded_answer"],
        }

    calculation = margin_money_subsidy_calculator(**calculator_args)
    return {
        "mode": "calculator",
        "answer": (
            f"Estimated subsidy: Rs {calculation['subsidy_amount']:,.2f}; "
            f"own contribution: Rs {calculation['own_contribution']:,.2f}; "
            f"bank loan: Rs {calculation['bank_loan_amount']:,.2f}."
        ),
        "confidence": "high",
        "follow_up": "Confirm final eligibility and sanction terms with the lender.",
        "calculation": calculation,
        "citations": [{"source": "scheme records", "page": 1, "title": calculation["scheme"]}],
        "steps": ["validated_project_cost", "calculated_margin_money_subsidy"],
    }
