"""Dataset loading primitives."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class Document:
    id: str
    title: str
    text: str


@dataclass(frozen=True)
class Query:
    id: str
    question: str
    relevant_doc_ids: tuple[str, ...]
    relevant_chunk_ids: tuple[str, ...]
    answer_terms: tuple[str, ...]
    query_type: str = "fact_lookup"


def load_documents(path: str | Path) -> list[Document]:
    return [
        Document(id=row["id"], title=row["title"], text=row["text"])
        for row in _read_jsonl(path)
    ]


def load_queries(path: str | Path) -> list[Query]:
    return [
        Query(
            id=row["id"],
            question=row["question"],
            relevant_doc_ids=tuple(row["relevant_doc_ids"]),
            relevant_chunk_ids=tuple(row.get("relevant_chunk_ids", ())),
            answer_terms=tuple(row["answer_terms"]),
            query_type=row.get("query_type", "fact_lookup"),
        )
        for row in _read_jsonl(path)
    ]


def _read_jsonl(path: str | Path) -> list[dict]:
    rows = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows
