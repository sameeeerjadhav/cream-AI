"""FastAPI service for UdyamSathi scheme records."""

from typing import Any

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from app.smart_search import load_records, search_records

app = FastAPI(title="UdyamSathi API")
records = load_records()


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)


class AskRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=10)


class CalculatorRequest(BaseModel):
    project_cost: float = Field(gt=0)
    activity_type: str
    category: str
    rural_urban: str
    scheme: str


class AgentRequest(BaseModel):
    question: str = Field(min_length=1)
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
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


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
def ask_question(request: QuestionRequest) -> dict[str, Any]:
    matches = search_records(records, request.question, limit=3)
    return {"question": request.question, "matches": matches}


@app.post("/chat")
def chat_endpoint(request: ChatRequest) -> dict[str, str]:
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
    return {
        "answer": result.answer,
        "confidence": result.confidence,
        "follow_up": result.follow_up,
    }


@app.post("/ask")
def ask_endpoint(request: AskRequest) -> dict[str, Any]:
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
    return {
        "question": request.question,
        "answer": result.answer,
        "confidence": result.confidence,
        "follow_up": result.follow_up,
        "citations": result.citations,
    }


@app.post("/agent")
def agent_endpoint(request: AgentRequest) -> dict[str, Any]:
    from app.graph import run_graph

    calculator_args = (
        request.calculator.model_dump() if request.calculator is not None else None
    )
    try:
        return run_graph(
            request.question,
            calculator_args,
            request.approved,
            request.thread_id,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
