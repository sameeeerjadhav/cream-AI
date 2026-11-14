"""Chunk downloaded UdyamSathi HTML documents with source metadata."""

from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
import re


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    text: str
    source: str
    page: int
    title: str


class _TextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []
        self._in_title = False
        self._ignored_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "title":
            self._in_title = True
        elif tag.lower() in {"script", "style", "noscript"}:
            self._ignored_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False
        elif tag.lower() in {"script", "style", "noscript"}:
            self._ignored_depth = max(0, self._ignored_depth - 1)

    def handle_data(self, data: str) -> None:
        if self._ignored_depth:
            return
        value = " ".join(data.split())
        if not value:
            return
        if self._in_title:
            self.title_parts.append(value)
        else:
            self.text_parts.append(value)


def _chunks(words: list[str], size: int, overlap: int) -> list[list[str]]:
    result: list[list[str]] = []
    step = size - overlap
    for start in range(0, len(words), step):
        result.append(words[start : start + size])
        if start + size >= len(words):
            break
    return result


def chunk_document(path: Path, size: int = 180, overlap: int = 30) -> list[DocumentChunk]:
    parser = _TextParser()
    parser.feed(path.read_text(encoding="utf-8"))
    title = " ".join(parser.title_parts).strip() or path.stem
    text = re.sub(r"\s+", " ", " ".join(parser.text_parts)).strip()
    parts = _chunks(text.split(), size, overlap)
    return [
        DocumentChunk(
            chunk_id=f"{path.stem}-{index}",
            text=" ".join(words),
            source=path.name,
            page=1,
            title=title,
        )
        for index, words in enumerate(parts)
        if words
    ]


def chunk_documents(raw_dir: Path = Path("data/raw")) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []
    for path in sorted(raw_dir.glob("*.html")):
        chunks.extend(chunk_document(path))
    return chunks
