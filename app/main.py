"""FastAPI service for UdyamSathi scheme records."""

import time
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Response
from pydantic import BaseModel, Field

from app.cache import query_cache
from app.observability import log_request_telemetry
from app.security import MAX_QUESTION_LENGTH, validate_question
from app.smart_search import load_records, search_records

app = FastAPI(title="UdyamSathi API")
records = load_records()


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=MAX_QUESTION_LENGTH)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=MAX_QUESTION_LENGTH)


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=MAX_QUESTION_LENGTH)
    top_k: int = Field(default=5, ge=1, le=10)


class CalculatorRequest(BaseModel):
    project_cost: float = Field(gt=0)
    activity_type: str
    category: str
    rural_urban: str
    scheme: str


class AgentRequest(BaseModel):
    question: str = Field(min_length=1, max_length=MAX_QUESTION_LENGTH)
    calculator: CalculatorRequest | None = None
    approved: bool = False
    thread_id: str = Field(default="default", min_length=1, max_length=100)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Welcome to UdyamSathi API",
        "health": "/health",
        "docs": "/docs",
        "records": "/records",
        "telemetry": "/cache/stats",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/cache/stats")
def cache_stats() -> dict[str, Any]:
    return query_cache.stats()


@app.get("/records")
def list_records(
    limit: int = Query(default=10, ge=1, le=100),
) -> list[dict[str, Any]]:
    return records[:limit]


@app.get("/records/{record_id}")
def get_record(record_id: str) -> dict[str, Any]:
    for record in records:
        if record["id"] == record_id:
            return record
    raise HTTPException(status_code=404, detail="Record not found")


@app.get("/search")
def search(
    q: str = Query(min_length=1),
    limit: int = Query(default=10, ge=1, le=100),
) -> list[dict[str, Any]]:
    return search_records(records, q, limit)


@app.get("/search/semantic")
def semantic_search_endpoint(
    q: str = Query(min_length=1),
    limit: int = Query(default=5, ge=1, le=20),
) -> list[dict[str, Any]]:
    from app.vectorstore import semantic_search

    return semantic_search(q, limit)


@app.post("/questions")
def ask_question(request: QuestionRequest, response: Response) -> dict[str, Any]:
    start = time.perf_counter()
    try:
        validate_question(request.question)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err

    matches = search_records(records, request.question, limit=3)
    latency_ms = (time.perf_counter() - start) * 1000
    telemetry = log_request_telemetry(
        "/questions",
        latency_ms,
        prompt_text=request.question,
        completion_text=str(matches),
        cached=False,
    )
    response.headers["X-Latency-Ms"] = str(telemetry["latency_ms"])
    response.headers["X-Tokens-Estimated"] = str(telemetry["total_tokens"])
    response.headers["X-Cache"] = "BYPASS"
    return {"question": request.question, "matches": matches}


@app.post("/chat")
def chat_endpoint(request: ChatRequest, response: Response) -> dict[str, str]:
    start = time.perf_counter()
    try:
        validate_question(request.question)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err

    from app.llm import (
        LLMConfigurationError,
        LLMProviderError,
        LLMResponseError,
        chat,
    )

    context = search_records(records, request.question, limit=3)
    try:
        result = chat(request.question, context)
    except (LLMConfigurationError, LLMProviderError, LLMResponseError) as error:
        raise HTTPException(status_code=503, detail=str(error)) from error

    latency_ms = (time.perf_counter() - start) * 1000
    telemetry = log_request_telemetry(
        "/chat",
        latency_ms,
        prompt_text=request.question,
        completion_text=result.answer,
        cached=False,
    )
    response.headers["X-Latency-Ms"] = str(telemetry["latency_ms"])
    response.headers["X-Tokens-Estimated"] = str(telemetry["total_tokens"])
    response.headers["X-Cache"] = "MISS"
    return {
        "answer": result.answer,
        "confidence": result.confidence,
        "follow_up": result.follow_up,
    }


@app.post("/ask")
def ask_endpoint(request: AskRequest, response: Response) -> dict[str, Any]:
    start = time.perf_counter()
    try:
        validate_question(request.question)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err

    cache_key = f"ask:{request.question.strip().casefold()}:{request.top_k}"
    cached = query_cache.get(cache_key)
    if cached is not None:
        latency_ms = (time.perf_counter() - start) * 1000
        telemetry = log_request_telemetry(
            "/ask",
            latency_ms,
            cached=True,
        )
        response.headers["X-Latency-Ms"] = str(telemetry["latency_ms"])
        response.headers["X-Tokens-Estimated"] = "0"
        response.headers["X-Cache"] = "HIT"
        return cached

    from app.llm import (
        LLMConfigurationError,
        LLMProviderError,
        LLMResponseError,
    )
    from app.rag import answer_question

    try:
        result = answer_question(request.question, top_k=request.top_k)
    except (LLMConfigurationError, LLMProviderError, LLMResponseError) as error:
        raise HTTPException(status_code=503, detail=str(error)) from error

    payload = {
        "question": request.question,
        "answer": result.answer,
        "confidence": result.confidence,
        "follow_up": result.follow_up,
        "citations": result.citations,
    }
    query_cache.set(cache_key, payload)

    latency_ms = (time.perf_counter() - start) * 1000
    telemetry = log_request_telemetry(
        "/ask",
        latency_ms,
        prompt_text=request.question,
        completion_text=result.answer,
        cached=False,
    )
    response.headers["X-Latency-Ms"] = str(telemetry["latency_ms"])
    response.headers["X-Tokens-Estimated"] = str(telemetry["total_tokens"])
    response.headers["X-Cache"] = "MISS"
    return payload


@app.post("/agent")
def agent_endpoint(request: AgentRequest, response: Response) -> dict[str, Any]:
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
