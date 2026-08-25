"""Typed domain models and input validation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class DatasetError(ValueError):
    """Raised when a corpus or evaluation set violates its schema."""


def _required_string(record: dict[str, Any], key: str, source: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise DatasetError(f"{source}: '{key}' must be a non-empty string")
    return value.strip()


@dataclass(frozen=True, slots=True)
class Document:
    """A versioned knowledge-base document."""

    id: str
    title: str
    text: str
    metadata: dict[str, Any]

    @classmethod
    def from_dict(cls, record: dict[str, Any], source: str) -> "Document":
        metadata = record.get("metadata", {})
        if not isinstance(metadata, dict):
            raise DatasetError(f"{source}: 'metadata' must be an object")
        return cls(
            id=_required_string(record, "id", source),
            title=_required_string(record, "title", source),
            text=_required_string(record, "text", source),
            metadata=metadata,
        )


@dataclass(frozen=True, slots=True)
class EvaluationQuery:
    """A query with binary relevance judgments and a reference answer."""

    id: str
    query: str
    relevant_ids: tuple[str, ...]
    reference_answer: str

    @classmethod
    def from_dict(cls, record: dict[str, Any], source: str) -> "EvaluationQuery":
        relevant = record.get("relevant_ids")
        if (
            not isinstance(relevant, list)
            or not relevant
            or not all(isinstance(item, str) and item.strip() for item in relevant)
        ):
            raise DatasetError(f"{source}: 'relevant_ids' must be a non-empty string list")
        normalized = tuple(item.strip() for item in relevant)
        if len(set(normalized)) != len(normalized):
            raise DatasetError(f"{source}: 'relevant_ids' contains duplicates")
        return cls(
            id=_required_string(record, "id", source),
            query=_required_string(record, "query", source),
            relevant_ids=normalized,
            reference_answer=_required_string(record, "reference_answer", source),
        )


@dataclass(frozen=True, slots=True)
class SearchResult:
    """One ranked retrieval result."""

    document: Document
    score: float
    rank: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "document_id": self.document.id,
            "title": self.document.title,
            "score": round(self.score, 8),
            "rank": self.rank,
        }
