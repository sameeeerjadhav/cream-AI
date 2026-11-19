"""Input validation and security guards against prompt injection."""

import re

MAX_QUESTION_LENGTH = 500

PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+|any\s+|the\s+)?(previous|prior|above)\s+(instructions|prompts|rules|commands)",
    r"disregard\s+(all\s+|any\s+|the\s+)?(previous|prior|above)\s+(instructions|prompts|rules)",
    r"forget\s+(all\s+|any\s+|the\s+)?(previous|prior)\s+instructions",
    r"system\s+prompt",
    r"reveal\s+(the\s+|your\s+)?(system|internal)\s+(prompt|instructions)",
    r"you\s+are\s+now\s+in\s+developer\s+mode",
    r"dan\s+mode",
    r"jailbreak",
    r"bypass\s+all\s+(rules|restrictions|filters)",
]

_INJECTION_REGEX = re.compile("|".join(PROMPT_INJECTION_PATTERNS), re.IGNORECASE)


def validate_question(question: str) -> None:
    """Validate input constraints and guard against prompt injection."""
    cleaned = question.strip()
    if not cleaned:
        raise ValueError("Question cannot be empty or whitespace only")
    if len(cleaned) > MAX_QUESTION_LENGTH:
        raise ValueError(
            f"Question exceeds maximum length of {MAX_QUESTION_LENGTH} characters"
        )
    if is_prompt_injection(cleaned):
        raise ValueError(
            "Prompt injection attempt detected: instruction override patterns are prohibited"
        )


def is_prompt_injection(text: str) -> bool:
    """Detect common prompt-injection override attempts."""
    return bool(_INJECTION_REGEX.search(text))
