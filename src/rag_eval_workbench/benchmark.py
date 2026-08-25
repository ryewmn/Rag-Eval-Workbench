"""Benchmark orchestration and machine-readable regression gates."""

from __future__ import annotations

import json
import platform
import statistics
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .io import load_documents, load_queries, sha256_file, validate_relevance
from .metrics import (
    citation_precision,
    groundedness_proxy,
    ndcg_at_k,
    percentile,
    recall_at_k,
    reciprocal_rank,
)
from .retriever import BM25Retriever

QUALITY_METRICS = (
    "recall_at_k",
    "mrr_at_k",
    "ndcg_at_k",
    "citation_precision_at_k",
    "groundedness_proxy_at_k",
)


@dataclass(frozen=True, slots=True)
class BenchmarkResult:
    """The result payload plus regression gate status."""

    payload: dict[str, Any]
    passed: bool


def _mean(values: list[float]) -> float:
    return statistics.fmean(values) if values else 0.0


def _round(value: float) -> float:
    return round(value, 6)


def load_thresholds(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {"minimum": {}, "maximum": {}}
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("regression config must contain a JSON object")
    minimum = value.get("minimum", {})
    maximum = value.get("maximum", {})
    if not isinstance(minimum, dict) or not isinstance(maximum, dict):
        raise ValueError("regression config minimum and maximum must be objects")
    return {"minimum": minimum, "maximum": maximum}


def evaluate_thresholds(
    metrics: dict[str, float], thresholds: dict[str, Any]
) -> list[dict[str, Any]]:
    """Return explicit pass/fail evidence for every configured threshold."""

    checks: list[dict[str, Any]] = []
    for direction, operator in (("minimum", ">="), ("maximum", "<=")):
        configured = thresholds.get(direction, {})
        for metric, threshold in sorted(configured.items()):
            if metric not in metrics:
                raise ValueError(f"threshold references unknown metric '{metric}'")
            if not isinstance(threshold, (int, float)):
                raise ValueError(f"threshold for '{metric}' must be numeric")
            actual = metrics[metric]
            passed = actual >= threshold if direction == "minimum" else actual <= threshold
            checks.append(
                {
                    "metric": metric,
                    "operator": operator,
                    "threshold": threshold,
                    "actual": actual,
                    "passed": passed,
                }
            )
    return checks


def run_benchmark(
    corpus_path: Path,
    queries_path: Path,
    *,
    k: int = 3,
    thresholds_path: Path | None = None,
    clock: Any = time.perf_counter,
) -> BenchmarkResult:
    """Run deterministic retrieval evaluation over a versioned dataset."""

    if k <= 0:
        raise ValueError("k must be positive")
    documents = load_documents(corpus_path)
    queries = load_queries(queries_path)
    validate_relevance(documents, queries)
    retriever = BM25Retriever(documents)
    per_query: list[dict[str, Any]] = []
    latencies: list[float] = []

    for query in queries:
        started = clock()
        results = retriever.search(query.query, k=k)
        elapsed_ms = max(0.0, (clock() - started) * 1000)
        latencies.append(elapsed_ms)
        retrieved_ids = [result.document.id for result in results]
        relevant_ids = set(query.relevant_ids)
        query_metrics = {
            "recall_at_k": recall_at_k(retrieved_ids, relevant_ids, k),
            "mrr_at_k": reciprocal_rank(retrieved_ids, relevant_ids, k),
            "ndcg_at_k": ndcg_at_k(retrieved_ids, relevant_ids, k),
            "citation_precision_at_k": citation_precision(retrieved_ids, relevant_ids, k),
            "groundedness_proxy_at_k": groundedness_proxy(
                query.reference_answer, [result.document for result in results]
            ),
        }
        per_query.append(
            {
                "query_id": query.id,
                "retrieved": [result.to_dict() for result in results],
                "metrics": {key: _round(value) for key, value in query_metrics.items()},
                "latency_ms": _round(elapsed_ms),
            }
        )

    aggregate = {
        metric: _round(_mean([item["metrics"][metric] for item in per_query]))
        for metric in QUALITY_METRICS
    }
    aggregate.update(
        {
            "latency_p50_ms": _round(percentile(latencies, 0.50)),
            "latency_p95_ms": _round(percentile(latencies, 0.95)),
        }
    )
    thresholds = load_thresholds(thresholds_path)
    checks = evaluate_thresholds(aggregate, thresholds)
    passed = all(check["passed"] for check in checks)
    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "system": {
            "retriever": "bm25",
            "parameters": {"k": k, "k1": retriever.k1, "b": retriever.b},
            "python": platform.python_version(),
        },
        "dataset": {
            "corpus_path": str(corpus_path),
            "queries_path": str(queries_path),
            "corpus_sha256": sha256_file(corpus_path),
            "queries_sha256": sha256_file(queries_path),
            "document_count": len(documents),
            "query_count": len(queries),
        },
        "metrics": aggregate,
        "regression_gate": {"passed": passed, "checks": checks},
        "queries": per_query,
    }
    return BenchmarkResult(payload=payload, passed=passed)
