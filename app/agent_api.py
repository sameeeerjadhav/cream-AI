"""FastAPI agent endpoint definition for UdyamSathi.

Implements POST /agent with LangGraph agent loop, MemorySaver,
and approval step validation.
"""

from __future__ import annotations

import time
from typing import Any

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, Field

from app.observability import log_request_telemetry
from app.security import MAX_QUESTION_LENGTH, validate_question

router = APIRouter(tags=["agent"])


class CalculatorPayload(BaseModel):
    scheme: str = Field(min_length=1)
    project_cost: float = Field(gt=0)
    category: str = Field(min_length=1)
    location: str = Field(min_length=1)
    industry_type: str = Field(default="manufacturing")


class AgentPayload(BaseModel):
    question: str = Field(min_length=1, max_length=MAX_QUESTION_LENGTH)
    calculator: CalculatorPayload | None = None
    approved: bool = False
    thread_id: str = Field(default="default", min_length=1, max_length=100)


@router.post("/agent")
def agent_endpoint(request: AgentPayload, response: Response) -> dict[str, Any]:
    """Execute LangGraph agent workflow with checkpointing and human-in-the-loop approval."""
    start = time.perf_counter()
    try:
        validate_question(request.question)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err

    from app.graph import run_graph

    calculator_args = (
        request.calculator.model_dump() if request.calculator is not None else None
    )
    try:
        res = run_graph(
            request.question,
            calculator_args,
            request.approved,
            request.thread_id,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    latency_ms = (time.perf_counter() - start) * 1000
    telemetry = log_request_telemetry(
        "/agent",
        latency_ms,
        prompt_text=request.question,
        completion_text=str(res.get("answer", "")),
        cached=False,
    )
    response.headers["X-Latency-Ms"] = str(telemetry["latency_ms"])
    response.headers["X-Tokens-Estimated"] = str(telemetry["total_tokens"])
    return res
