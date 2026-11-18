"""Lightweight Vercel entrypoint for UdyamSathi."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException

app = FastAPI(title="UdyamSathi API")


ROOT = Path(__file__).resolve().parents[1]
SPEC = spec_from_file_location(
    "udyamsaathi_sample_records", ROOT / "data" / "sample_records.py"
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Unable to load UdyamSathi records")
RECORDS_MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(RECORDS_MODULE)
RECORDS: list[dict[str, Any]] = RECORDS_MODULE.RECORDS


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/records")
def list_records(limit: int = 10) -> list[dict[str, Any]]:
    return RECORDS[: max(1, min(limit, 100))]


@app.get("/records/{record_id}")
def get_record(record_id: str) -> dict[str, Any]:
    for record in RECORDS:
        if record["id"] == record_id:
            return record
    raise HTTPException(status_code=404, detail="Record not found")
