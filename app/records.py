# Record loading and lookup helpers.

from collections import Counter
from typing import Any

from data.sample_records import RECORDS


def load_records() -> list[dict[str, Any]]:
    return [record.copy() for record in RECORDS]


def search(records: list[dict[str, Any]], keyword: str) -> list[dict[str, Any]]:
    term = keyword.strip().casefold()
    if not term:
        return []
    return [
        record
        for record in records
        if term in " ".join(str(value) for value in record.values()).casefold()
    ]


def count_by(records: list[dict[str, Any]], field: str = "category") -> dict[str, int]:
    return dict(Counter(str(record.get(field, "")) for record in records))


def get_by_id(records: list[dict[str, Any]], record_id: str) -> dict[str, Any] | None:
    return next((record for record in records if record.get("id") == record_id), None)
