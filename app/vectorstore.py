"""Persistent Chroma vector store for UdyamSathi document chunks."""

from pathlib import Path
from typing import Any

import chromadb

from app.chunking import chunk_documents
from app.embed import embed_texts

CHROMA_PATH = Path("data/chroma")
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
