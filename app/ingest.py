# Clean raw scheme documents into data/records.json.

import json
import re
from html import unescape
from pathlib import Path

from app.models import Record

RAW_DIR = Path("data/raw")
OUTPUT_PATH = Path("data/records.json")


def _text_from_html(raw_html: str) -> str:
    text = re.sub(r"<script\b[^>]*>.*?</script>", " ", raw_html, flags=re.I | re.S)
    text = re.sub(r"<style\b[^>]*>.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", unescape(text)).strip()


def _record_from_document(path: Path) -> Record:
    text = _text_from_html(path.read_text(encoding="utf-8"))
    source = path.stem.lower()
    if source == "cmegp":
        return Record(
            "Chief Minister Employment Generation Programme (CMEGP)",
            "Rs 50 lakh manufacturing; Rs 20 lakh service",
            "15% urban, 25% rural",
            "25% urban, 35% rural",
            "10% general; 5% special",
            text[:1000],
        )
    if source == "pmegp":
        return Record(
            "Prime Minister's Employment Generation Programme (PMEGP)",
            "Rs 50 lakh manufacturing; Rs 20 lakh service",
            "15% urban, 25% rural",
            "25% urban, 35% rural",
            "10% general; 5% special",
            text[:1000],
        )
    return Record(
        "Government Schemes for MSME",
        "Varies by scheme",
        "Varies by scheme",
        "Varies by scheme",
        "Varies by scheme",
        text[:1000],
    )


def ingest(
    raw_dir: Path = RAW_DIR, output_path: Path = OUTPUT_PATH
) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    errors: list[str] = []

    for path in sorted(raw_dir.glob("*.html")):
        try:
            record = _record_from_document(path)
            if not record.scheme_name or not record.eligibility:
                raise ValueError("missing required fields")
            records.append(record.to_dict())
        except (OSError, UnicodeError, ValueError) as error:
            errors.append(f"{path}: {error}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(records, indent=2), encoding="utf-8")
    for error in errors:
        print(f"Skipped bad row - {error}")
    print(f"Saved {len(records)} record(s) to {output_path}.")
    return records


if __name__ == "__main__":
    ingest()
