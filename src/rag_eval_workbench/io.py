"""Dataset loading, integrity checks, and safe artifact output."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Callable, TypeVar

from .models import DatasetError, Document, EvaluationQuery

T = TypeVar("T")


def _read_jsonl(path: Path, parser: Callable[[dict[str, Any], str], T]) -> list[T]:
    if not path.is_file():
        raise DatasetError(f"dataset file does not exist: {path}")
    records: list[T] = []
    seen_ids: set[str] = set()
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            source = f"{path}:{line_number}"
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise DatasetError(f"{source}: invalid JSON: {exc.msg}") from exc
            if not isinstance(value, dict):
                raise DatasetError(f"{source}: each line must be a JSON object")
            parsed = parser(value, source)
            record_id = getattr(parsed, "id")
            if record_id in seen_ids:
                raise DatasetError(f"{source}: duplicate id '{record_id}'")
            seen_ids.add(record_id)
            records.append(parsed)
    if not records:
        raise DatasetError(f"dataset file is empty: {path}")
    return records


def load_documents(path: Path) -> list[Document]:
    """Load and validate corpus documents from JSONL."""

    return _read_jsonl(path, Document.from_dict)


def load_queries(path: Path) -> list[EvaluationQuery]:
    """Load and validate evaluation queries from JSONL."""

    return _read_jsonl(path, EvaluationQuery.from_dict)


def validate_relevance(documents: list[Document], queries: list[EvaluationQuery]) -> None:
    """Ensure every relevance judgment resolves to a corpus document."""

    document_ids = {document.id for document in documents}
    for query in queries:
        missing = set(query.relevant_ids) - document_ids
        if missing:
            raise DatasetError(
                f"query '{query.id}' references unknown document ids: {sorted(missing)}"
            )


def sha256_file(path: Path) -> str:
    """Return a stable dataset fingerprint."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    """Write JSON by atomic replacement so interrupted runs do not corrupt artifacts."""

    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise
