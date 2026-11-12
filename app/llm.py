"""Provider wrapper for Groq and Gemini chat completion APIs."""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()

PROMPTS_DIR = Path("prompts")


class LLMConfigurationError(RuntimeError):
    """Raised when the selected provider is not configured."""


class LLMResponseError(RuntimeError):
    """Raised when a provider response cannot be interpreted."""


@dataclass(frozen=True)
class ChatResult:
    answer: str
    confidence: str
    follow_up: str


def _prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8").strip()


def _provider_config() -> tuple[str, str, str]:
    provider = os.getenv("LLM_PROVIDER", "groq").casefold()
    if provider == "groq":
        key = os.getenv("GROQ_API_KEY", "")
        model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    elif provider == "gemini":
        key = os.getenv("GEMINI_API_KEY", "")
        model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    else:
        raise LLMConfigurationError(
            "LLM_PROVIDER must be either 'groq' or 'gemini'"
        )
    if not key:
        raise LLMConfigurationError(f"Missing API key for provider '{provider}'")
    return provider, key, model


def _request_provider(
    provider: str, key: str, model: str, system_prompt: str, user_prompt: str
) -> str:
    if provider == "groq":
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={
                "model": model,
                "temperature": 0.2,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            },
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        return payload["choices"][0]["message"]["content"]

    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        params={"key": key},
        json={
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {"temperature": 0.2},
        },
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    return payload["candidates"][0]["content"]["parts"][0]["text"]


def _parse_result(raw: str) -> ChatResult:
    candidate = raw.strip()
    if candidate.startswith("```"):
        candidate = candidate.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    try:
        payload: Any = json.loads(candidate)
        result = ChatResult(
            answer=str(payload["answer"]).strip(),
            confidence=str(payload["confidence"]).strip(),
            follow_up=str(payload["follow_up"]).strip(),
        )
    except (ValueError, KeyError, TypeError) as error:
        raise LLMResponseError("Provider returned invalid chat JSON") from error
    if not all((result.answer, result.confidence, result.follow_up)):
        raise LLMResponseError("Provider returned incomplete chat JSON")
    return result


def chat(question: str, context: list[dict[str, Any]]) -> ChatResult:
    """Ask the configured provider using retrieved UdyamSathi context."""
    provider, key, model = _provider_config()
    user_prompt = _prompt("task_chat.txt").format(
        question=question,
        context=json.dumps(context, ensure_ascii=False, indent=2),
    )
    raw = _request_provider(
        provider, key, model, _prompt("system.txt"), user_prompt
    )
    return _parse_result(raw)
