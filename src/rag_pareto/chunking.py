"""Document chunking."""

from __future__ import annotations

from dataclasses import dataclass

from .data import Document
from .text import tokenize


@dataclass(frozen=True)
class Chunk:
    id: str
    doc_id: str
    title: str
    text: str


def chunk_documents(documents: list[Document], size_tokens: int, overlap_tokens: int) -> list[Chunk]:
    if size_tokens <= 0:
        raise ValueError("size_tokens must be positive")
    if overlap_tokens < 0 or overlap_tokens >= size_tokens:
        raise ValueError("overlap_tokens must be non-negative and smaller than size_tokens")

    chunks: list[Chunk] = []
    step = size_tokens - overlap_tokens
    for document in documents:
        tokens = tokenize(document.text)
        if not tokens:
            continue
        for index, start in enumerate(range(0, len(tokens), step)):
            window = tokens[start : start + size_tokens]
            if not window:
                break
            chunk_id = f"{document.id}::c{index:03d}"
            chunks.append(Chunk(id=chunk_id, doc_id=document.id, title=document.title, text=" ".join(window)))
            if start + size_tokens >= len(tokens):
                break
    return chunks

