"""Telemetry and token tracking for UdyamSathi API requests."""

import logging
from typing import Any

logger = logging.getLogger("udyamsaathi.telemetry")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [telemetry] %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def estimate_tokens(text: str) -> int:
    """Heuristic token count estimation (~4 characters per token)."""
    if not text:
        return 0
    return max(1, len(text.strip()) // 4)


def log_request_telemetry(
    endpoint: str,
    latency_ms: float,
    prompt_text: str = "",
    completion_text: str = "",
    cached: bool = False,
) -> dict[str, Any]:
    """Log structured telemetry data for latency and token consumption."""
    prompt_tokens = 0 if cached else estimate_tokens(prompt_text)
    completion_tokens = 0 if cached else estimate_tokens(completion_text)
    total_tokens = prompt_tokens + completion_tokens

    telemetry = {
        "endpoint": endpoint,
        "latency_ms": round(latency_ms, 2),
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "cached": cached,
    }

    logger.info(
        "endpoint=%s latency_ms=%.2f prompt_tokens=%d completion_tokens=%d total_tokens=%d cached=%s",
        endpoint,
        telemetry["latency_ms"],
        prompt_tokens,
        completion_tokens,
        total_tokens,
        cached,
    )
    return telemetry
