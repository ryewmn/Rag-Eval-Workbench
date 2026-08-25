"""Simple, auditable English tokenizer for the lexical baseline."""

from __future__ import annotations

import re

TOKEN_PATTERN = re.compile(r"[a-z0-9]+(?:['-][a-z0-9]+)?")
STOP_WORDS = frozenset(
    {
        "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "how",
        "in", "is", "it", "of", "on", "or", "that", "the", "this", "to", "was",
        "what", "when", "where", "which", "with",
    }
)


def tokenize(text: str, *, remove_stop_words: bool = False) -> list[str]:
    """Lowercase and extract alphanumeric tokens without external NLP dependencies."""

    tokens = TOKEN_PATTERN.findall(text.lower())
    if remove_stop_words:
        return [token for token in tokens if token not in STOP_WORDS]
    return tokens
