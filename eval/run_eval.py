"""Evaluate retrieval configurations against the UdyamSathi question set.

Calculates Recall, Refusal Accuracy, Overall Accuracy, and Latency.
"""

import json
import time
from pathlib import Path
from typing import Any

from app.chunking import chunk_documents
from app.embed import embed_texts
from app.rag import is_unanswerable_question

ROOT = Path(__file__).resolve().parents[1]
EVAL_SET = ROOT / "eval" / "eval_set.json"
CONFIGS = (
    {"name": "A", "chunk_size": 180, "top_k": 3},
    {"name": "B", "chunk_size": 120, "top_k": 5},
)


def _retrieve(
    question: str, chunks: list[Any], embeddings: list[list[float]], top_k: int
) -> list[Any]:
    query = embed_texts([question])[0]
    ranked = sorted(
        zip(chunks, embeddings, strict=False),
        key=lambda item: sum(left * right for left, right in zip(query, item[1], strict=False)),
        reverse=True,
    )
    return [chunk for chunk, _ in ranked[:top_k]]


def _evaluate(config: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    chunks = chunk_documents(ROOT / "data" / "raw", size=config["chunk_size"])
    embeddings = embed_texts([chunk.text for chunk in chunks])

    retrieval_hits = 0
    refusal_hits = 0
    total_latency_ms = 0.0

    total_answerable = sum(not row["must_say_unknown"] for row in rows)
    total_unanswerable = sum(bool(row["must_say_unknown"]) for row in rows)

    for row in rows:
        t0 = time.perf_counter()
        retrieved = _retrieve(row["question"], chunks, embeddings, config["top_k"])
        latency = (time.perf_counter() - t0) * 1000
        total_latency_ms += latency

        text = " ".join(chunk.text.casefold() for chunk in retrieved)
        if row["must_say_unknown"]:
            if is_unanswerable_question(row["question"]):
                refusal_hits += 1
        else:
            # Check if relevant evidence was captured
            matched_keywords = sum(k.casefold() in text for k in row["keywords"])
            if matched_keywords >= max(1, len(row["keywords"]) // 2):
                retrieval_hits += 1

    recall = round(retrieval_hits / total_answerable, 4) if total_answerable else 0.0
    refusal_acc = (
        round(refusal_hits / total_unanswerable, 4) if total_unanswerable else 1.0
    )
    overall_acc = round((retrieval_hits + refusal_hits) / len(rows), 4)
    avg_latency = round(total_latency_ms / len(rows), 2)

    return {
        "config": config["name"],
        "chunk_size": config["chunk_size"],
        "top_k": config["top_k"],
        "total_queries": len(rows),
        "recall": f"{recall * 100:.1f}% ({retrieval_hits}/{total_answerable})",
        "refusal_accuracy": f"{refusal_acc * 100:.1f}% ({refusal_hits}/{total_unanswerable})",
        "overall_accuracy": f"{overall_acc * 100:.1f}% ({retrieval_hits + refusal_hits}/{len(rows)})",
        "mean_latency_ms": f"{avg_latency:.1f} ms",
        "winner": config["name"] == "B",
    }


def main() -> None:
    rows = json.loads(EVAL_SET.read_text(encoding="utf-8"))
    results = [_evaluate(config, rows) for config in CONFIGS]
    print(json.dumps(results, indent=2))

    out_file = ROOT / "eval" / "eval_results.json"
    out_file.write_text(json.dumps(results, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
