"""Deterministic Okapi BM25 retrieval baseline."""

from __future__ import annotations

import math
from collections import Counter

from .models import Document, SearchResult
from .tokenize import tokenize


class BM25Retriever:
    """A small in-memory BM25 index with stable tie-breaking.

    Scores use the Robertson-Sparck Jones IDF variant with a positive offset.
    Equal scores are ordered by document id to keep benchmark artifacts reproducible.
    """

    def __init__(
        self,
        documents: list[Document],
        *,
        k1: float = 1.5,
        b: float = 0.75,
    ) -> None:
        if not documents:
            raise ValueError("documents cannot be empty")
        if k1 <= 0:
            raise ValueError("k1 must be positive")
        if not 0 <= b <= 1:
            raise ValueError("b must be between 0 and 1")
        self.documents = tuple(documents)
        self.k1 = k1
        self.b = b
        self._term_frequencies = [
            Counter(tokenize(f"{document.title} {document.text}"))
            for document in self.documents
        ]
        self._lengths = [sum(frequencies.values()) for frequencies in self._term_frequencies]
        self._average_length = sum(self._lengths) / len(self._lengths)
        document_frequency: Counter[str] = Counter()
        for frequencies in self._term_frequencies:
            document_frequency.update(frequencies.keys())
        count = len(self.documents)
        self._idf = {
            term: math.log(1.0 + (count - frequency + 0.5) / (frequency + 0.5))
            for term, frequency in document_frequency.items()
        }

    def search(self, query: str, *, k: int = 5) -> list[SearchResult]:
        """Return the top-k documents for a non-empty query."""

        if k <= 0:
            raise ValueError("k must be positive")
        query_terms = tokenize(query)
        if not query_terms:
            return []
        scores: list[tuple[float, Document]] = []
        for index, document in enumerate(self.documents):
            frequencies = self._term_frequencies[index]
            length = self._lengths[index]
            score = 0.0
            for term in query_terms:
                term_frequency = frequencies.get(term, 0)
                if not term_frequency:
                    continue
                denominator = term_frequency + self.k1 * (
                    1 - self.b + self.b * length / self._average_length
                )
                score += self._idf.get(term, 0.0) * (
                    term_frequency * (self.k1 + 1) / denominator
                )
            scores.append((score, document))
        scores.sort(key=lambda item: (-item[0], item[1].id))
        return [
            SearchResult(document=document, score=score, rank=rank)
            for rank, (score, document) in enumerate(scores[:k], start=1)
        ]
