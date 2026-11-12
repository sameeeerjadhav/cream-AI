"""FastAPI service for UdyamSathi scheme records."""

from typing import Any

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from app.llm import LLMConfigurationError, LLMResponseError, chat
from app.smart_search import load_records, search_records

app = FastAPI(title="UdyamSathi API")
records = load_records()


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)


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


@app.post("/questions")
def ask_question(request: QuestionRequest) -> dict[str, Any]:
    matches = search_records(records, request.question, limit=3)
    return {"question": request.question, "matches": matches}


@app.post("/chat")
def chat_endpoint(request: ChatRequest) -> dict[str, str]:
    context = search_records(records, request.question, limit=3)
    try:
        result = chat(request.question, context)
    except (LLMConfigurationError, LLMResponseError) as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    return {
        "answer": result.answer,
        "confidence": result.confidence,
        "follow_up": result.follow_up,
    }
