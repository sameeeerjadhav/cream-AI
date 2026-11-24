"""TF-IDF search over the cleaned UdyamSathi records."""

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RECORDS_PATH = ROOT / "data" / "records.json"


def record_id(record: dict[str, Any]) -> str:
    """Return a stable URL-safe identifier for a record."""
    identifier = re.sub(r"[^a-z0-9]+", "-", record["scheme_name"].lower()).strip("-")
    return identifier


def load_records(path: Path | None = None) -> list[dict[str, Any]]:
    target_path = Path(path) if path is not None else RECORDS_PATH
    records = json.loads(target_path.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise TypeError(f"{target_path} must contain a JSON list")
    return [{**record, "id": record_id(record)} for record in records]


def _search_text(record: dict[str, Any]) -> str:
    return " ".join(str(value) for key, value in record.items() if key != "id")


def search_records(
    records: list[dict[str, Any]], query: str, limit: int = 10
) -> list[dict[str, Any]]:
    """Return records ranked by relevance to a query."""
    query = query.strip()
    if not query:
        return []

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        documents = [_search_text(record) for record in records]
        vectorizer = TfidfVectorizer(stop_words="english")
        matrix = vectorizer.fit_transform(documents)
        scores = cosine_similarity(vectorizer.transform([query]), matrix)[0]
        ranked_indexes = sorted(
            range(len(records)), key=lambda index: scores[index], reverse=True
        )
        return [records[index] for index in ranked_indexes[:limit]]
    except ImportError:
        # High-resilience pure-Python fallback for environments without scikit-learn
        words = set(re.findall(r"\w+", query.casefold()))

        def score(record: dict[str, Any]) -> float:
            text = _search_text(record).casefold()
            return sum(text.count(w) for w in words)

        sorted_records = sorted(records, key=score, reverse=True)
        return sorted_records[:limit]
