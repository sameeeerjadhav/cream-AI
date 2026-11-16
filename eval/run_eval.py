"""Evaluate retrieval configurations against the UdyamSathi question set."""

import json
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
        zip(chunks, embeddings),
        key=lambda item: sum(left * right for left, right in zip(query, item[1])),
        reverse=True,
    )
    return [chunk for chunk, _ in ranked[:top_k]]


def _evaluate(config: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    chunks = chunk_documents(ROOT / "data" / "raw", size=config["chunk_size"])
    embeddings = embed_texts([chunk.text for chunk in chunks])
    retrieval_hits = 0
    unknown_correct = 0
    for row in rows:
        retrieved = _retrieve(row["question"], chunks, embeddings, config["top_k"])
        text = " ".join(chunk.text.casefold() for chunk in retrieved)
        if row["must_say_unknown"]:
            unknown_correct += int(is_unanswerable_question(row["question"]))
        elif all(keyword.casefold() in text for keyword in row["keywords"]):
            retrieval_hits += 1
    answerable = sum(not row["must_say_unknown"] for row in rows)
    return {
        **config,
        "questions": len(rows),
        "retrieval_hits": retrieval_hits,
        "retrieval_hit_rate": round(retrieval_hits / answerable, 3),
        "unknown_q6": f"{unknown_correct}/{sum(row['must_say_unknown'] for row in rows)}",
    }


def main() -> None:
    rows = json.loads(EVAL_SET.read_text(encoding="utf-8"))
    results = [_evaluate(config, rows) for config in CONFIGS]
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
