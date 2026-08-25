"""Retrieval, citation, grounding, and latency metrics."""

from __future__ import annotations

import math

from .models import Document
from .tokenize import tokenize


def recall_at_k(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> float:
    if not relevant_ids:
        return 0.0
    return len(set(retrieved_ids[:k]) & relevant_ids) / len(relevant_ids)


def reciprocal_rank(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> float:
    for rank, document_id in enumerate(retrieved_ids[:k], start=1):
        if document_id in relevant_ids:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> float:
    dcg = sum(
        1.0 / math.log2(rank + 1)
        for rank, document_id in enumerate(retrieved_ids[:k], start=1)
        if document_id in relevant_ids
    )
    ideal_hits = min(len(relevant_ids), k)
    ideal_dcg = sum(1.0 / math.log2(rank + 1) for rank in range(1, ideal_hits + 1))
    return dcg / ideal_dcg if ideal_dcg else 0.0


def citation_precision(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> float:
    """Precision if each retrieved context is treated as an emitted citation."""

    selected = retrieved_ids[:k]
    if not selected:
        return 0.0
    return sum(document_id in relevant_ids for document_id in selected) / len(selected)


def groundedness_proxy(reference_answer: str, retrieved_documents: list[Document]) -> float:
    """Fraction of unique reference-answer content tokens supported by contexts.

    This is an inexpensive lexical proxy, not a factuality or entailment judge.
    """

    answer_tokens = set(tokenize(reference_answer, remove_stop_words=True))
    if not answer_tokens:
        return 0.0
    context_tokens = set(
        tokenize(
            " ".join(f"{document.title} {document.text}" for document in retrieved_documents),
            remove_stop_words=True,
        )
    )
    return len(answer_tokens & context_tokens) / len(answer_tokens)


def percentile(values: list[float], quantile: float) -> float:
    """Linearly interpolated percentile compatible with NumPy's default method."""

    if not values:
        return 0.0
    if not 0 <= quantile <= 1:
        raise ValueError("quantile must be between 0 and 1")
    ordered = sorted(values)
    position = (len(ordered) - 1) * quantile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight
