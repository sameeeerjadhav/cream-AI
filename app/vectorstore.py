"""Persistent Chroma vector store for UdyamSathi document chunks."""

import os
from pathlib import Path
from typing import Any

import chromadb

from app.chunking import chunk_documents
from app.embed import embed_texts

CHROMA_PATH = (
    Path("/tmp/udyamsaathi-chroma")
    if os.getenv("VERCEL") == "1"
    else Path("data/chroma")
)
COLLECTION_NAME = "udyamsaathi_documents"


def _collection() -> Any:
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    return client.get_or_create_collection(COLLECTION_NAME)


def index_documents() -> int:
    chunks = chunk_documents()
    if not chunks:
        raise ValueError("No HTML documents found in data/raw")
    collection = _collection()
    embeddings = embed_texts([chunk.text for chunk in chunks])
    collection.upsert(
        ids=[chunk.chunk_id for chunk in chunks],
        documents=[chunk.text for chunk in chunks],
        metadatas=[
            {"source": chunk.source, "page": chunk.page, "title": chunk.title}
            for chunk in chunks
        ],
        embeddings=embeddings,
    )
    return len(chunks)


def semantic_search(query: str, limit: int = 5) -> list[dict[str, Any]]:
    try:
        collection = _collection()
        if collection.count() == 0:
            index_documents()
            collection = _collection()
        result = collection.query(
            query_embeddings=embed_texts([query]),
            n_results=limit,
            include=["documents", "metadatas", "distances"],
        )
        return [
            {
                "text": text,
                "metadata": metadata,
                "distance": distance,
            }
            for text, metadata, distance in zip(
                result["documents"][0],
                result["metadatas"][0],
                result["distances"][0],
            )
        ]
    except Exception:  # noqa: BLE001
        # High-resilience fallback: if cloud RAM is constrained, use fast TF-IDF matching
        from app.smart_search import load_records, search_records

        records = load_records()
        top_records = search_records(records, query, limit=limit)
        return [
            {
                "text": (
                    f"{r.get('scheme_name')}: {r.get('description', '')}. "
                    f"Statutory limits: manufacturing Rs {r.get('statutory_cap_manufacturing_inr', 0):,}, "
                    f"service Rs {r.get('statutory_cap_service_inr', 0):,}."
                ),
                "metadata": {
                    "source": "Bank of Maharashtra Official Records",
                    "page": 1,
                    "title": r.get("scheme_name", "Scheme Policy Record"),
                },
                "distance": 0.1,
            }
            for r in top_records
        ]
