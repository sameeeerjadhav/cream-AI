"""Retrieval-augmented answers for UdyamSathi questions."""

from dataclasses import dataclass
from typing import Any

from app.llm import (
    LLMConfigurationError,
    LLMProviderError,
    LLMResponseError,
    chat,
)
from app.vectorstore import semantic_search


@dataclass(frozen=True)
class RagResult:
    answer: str
    confidence: str
    follow_up: str
    citations: list[dict[str, Any]]


def is_unanswerable_question(question: str) -> bool:
    """Return whether the question needs live data unavailable to the service."""
    normalized = question.casefold()
    return any(
        phrase in normalized
        for phrase in (
            "application been approved",
            "loan application",
            "when will the money arrive",
            "disbursement date",
            "application status",
        )
    )


def _citations(hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    citations: list[dict[str, Any]] = []
    seen: set[tuple[str, int, str]] = set()
    for hit in hits:
        metadata = hit.get("metadata") or {}
        citation = {
            "source": str(metadata.get("source", "unknown")),
            "page": int(metadata.get("page", 1)),
            "title": str(metadata.get("title", "UdyamSathi source")),
        }
        key = (citation["source"], citation["page"], citation["title"])
        if key not in seen:
            citations.append(citation)
            seen.add(key)
    return citations


def answer_question(question: str, top_k: int = 5) -> RagResult:
    """Retrieve supporting chunks and answer with explicit source citations."""
    hits = semantic_search(question, limit=top_k)
    citations = _citations(hits)

    if is_unanswerable_question(question):
        return RagResult(
            answer=(
                "I don't know. UdyamSathi does not have live application "
                "status or disbursement data."
            ),
            confidence="low",
            follow_up="Please check with the bank or the official PMEGP portal.",
            citations=[],
        )
    if not hits:
        return RagResult(
            answer="I don't know. The available UdyamSathi sources do not answer this.",
            confidence="low",
            follow_up="Ask about a scheme, eligibility rule, subsidy, or project limit.",
            citations=[],
        )

    try:
        result = chat(question, hits)
    except (LLMConfigurationError, LLMProviderError, LLMResponseError):
        excerpts = [
            str(hit.get("text", "")).strip()
            for hit in hits[:2]
            if str(hit.get("text", "")).strip()
        ]
        evidence = " ".join(excerpts)
        if evidence:
            answer = (
                "The retrieved UdyamSathi sources contain relevant information, "
                f"but the answer-generation provider is unavailable. Evidence: {evidence[:900]}"
            )
        else:
            answer = "I don't know. No usable source evidence was retrieved."
        return RagResult(
            answer=answer,
            confidence="low",
            follow_up="Review the cited official source or try again when the provider is configured.",
            citations=citations,
        )

    source_labels = ", ".join(
        f"[{index}] {citation['source']} p.{citation['page']}"
        for index, citation in enumerate(citations, start=1)
    )
    answer = f"{result.answer}\n\nSources: {source_labels}"
    return RagResult(
        answer=answer,
        confidence=result.confidence,
        follow_up=result.follow_up,
        citations=citations,
    )
