"""TF-IDF search over the cleaned UdyamSathi records."""

import json
import re
from pathlib import Path
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

RECORDS_PATH = Path("data/records.json")


def record_id(record: dict[str, Any]) -> str:
    """Return a stable URL-safe identifier for a record."""
    identifier = re.sub(r"[^a-z0-9]+", "-", record["scheme_name"].lower()).strip("-")
    return identifier


def load_records(path: Path = RECORDS_PATH) -> list[dict[str, Any]]:
    records = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError(f"{path} must contain a JSON list")
    return [{**record, "id": record_id(record)} for record in records]


def _search_text(record: dict[str, Any]) -> str:
    return " ".join(str(value) for key, value in record.items() if key != "id")


def search_records(
    records: list[dict[str, Any]], query: str, limit: int = 10
) -> list[dict[str, Any]]:
    """Return records ranked by cosine similarity to a query."""
    query = query.strip()
    if not query:
        return []

    documents = [_search_text(record) for record in records]
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(documents)
    scores = cosine_similarity(vectorizer.transform([query]), matrix)[0]
    ranked_indexes = sorted(
        range(len(records)), key=lambda index: scores[index], reverse=True
    )
    return [records[index] for index in ranked_indexes[:limit]]
