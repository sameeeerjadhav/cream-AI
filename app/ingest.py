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
    text = re.sub(r"\s+", " ", unescape(text)).strip()
    return re.sub(r"(\d)\s+(st|nd|rd|th)\b", r"\1\2", text, flags=re.I)


def _eligibility_from_text(text: str, source: str) -> str:
    sections = {
        "cmegp": (
            r"6\)\s*Eligibility criteria under the scheme:",
            r"7\)\s*Other Eligibility Conditions under CMEGP:",
        ),
        "pmegp": (r"Eligible Borrowers", r"Repayment Tenor"),
        "mudra": (r"Eligibility Borrowers", r"5\s*Quantum of Finance"),
        "stand-up-india": (r"Eligibility", r"Nature of Loan"),
    }
    boundaries = sections.get(source)
    if boundaries is None:
        return "Eligibility details are not listed on the source page."

    start, end = boundaries
    match = re.search(
        rf"{start}\s*(.*?)(?={end})",
        text,
        flags=re.I | re.S,
    )
    if match is None:
        raise ValueError(f"eligibility section not found for {source}")

    eligibility = re.sub(r"\s+", " ", match.group(1)).strip(" .")
    if not eligibility:
        raise ValueError(f"eligibility section is empty for {source}")
    return eligibility


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
            _eligibility_from_text(text, source),
        )
    if source == "pmegp":
        return Record(
            "Prime Minister's Employment Generation Programme (PMEGP)",
            "Rs 50 lakh manufacturing; Rs 20 lakh service",
            "15% urban, 25% rural",
            "25% urban, 35% rural",
            "10% general; 5% special",
            _eligibility_from_text(text, source),
        )
    if source == "mudra":
        return Record(
            "Pradhan Mantri MUDRA Yojana (PMMY)",
            "Loan up to Rs 20 lakh",
            "Not applicable",
            "Not applicable",
            "As decided by the lender",
            _eligibility_from_text(text, source),
        )
    if source == "stand-up-india":
        return Record(
            "Stand-Up India",
            "Composite loan from Rs 10 lakh to Rs 1 crore",
            "Not applicable",
            "Not applicable",
            "At least 10% of project cost",
            _eligibility_from_text(text, source),
        )
    if source == "vishwakarma":
        return Record(
            "PM Vishwakarma",
            "Loan up to Rs 3 lakh in two tranches",
            "Interest subvention to 5% beneficiary rate",
            "Interest subvention to 5% beneficiary rate",
            "As specified under the scheme",
            "Artisans and craftspeople (Vishwakarma) for their respective trades.",
        )
    return Record(
        "Government Schemes for MSME",
        "Varies by scheme",
        "Varies by scheme",
        "Varies by scheme",
        "Varies by scheme",
        _eligibility_from_text(text, source),
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
