"""Command-line interface used locally and in CI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .benchmark import run_benchmark
from .io import load_documents, load_queries, validate_relevance, write_json_atomic
from .models import DatasetError
from .retriever import BM25Retriever


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rag-eval",
        description="Measure deterministic RAG retrieval quality and block regressions.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    benchmark = commands.add_parser("benchmark", help="run the evaluation suite")
    benchmark.add_argument("--corpus", type=Path, required=True)
    benchmark.add_argument("--queries", type=Path, required=True)
    benchmark.add_argument("--thresholds", type=Path)
    benchmark.add_argument("--output", type=Path, required=True)
    benchmark.add_argument("-k", type=int, default=3)

    search = commands.add_parser("search", help="inspect ranked results")
    search.add_argument("query")
    search.add_argument("--corpus", type=Path, required=True)
    search.add_argument("-k", type=int, default=3)

    validate = commands.add_parser("validate", help="validate corpus and judgments")
    validate.add_argument("--corpus", type=Path, required=True)
    validate.add_argument("--queries", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "benchmark":
            result = run_benchmark(
                args.corpus,
                args.queries,
                k=args.k,
                thresholds_path=args.thresholds,
            )
            write_json_atomic(args.output, result.payload)
            print(json.dumps(result.payload["metrics"], indent=2, sort_keys=True))
            if result.passed:
                print(f"PASS: regression gate passed; artifact: {args.output}")
                return 0
            print(f"FAIL: regression gate failed; artifact: {args.output}", file=sys.stderr)
            return 2
        if args.command == "search":
            retriever = BM25Retriever(load_documents(args.corpus))
            print(json.dumps([item.to_dict() for item in retriever.search(args.query, k=args.k)], indent=2))
            return 0
        documents = load_documents(args.corpus)
        queries = load_queries(args.queries)
        validate_relevance(documents, queries)
        print(f"PASS: {len(documents)} documents and {len(queries)} queries are valid")
        return 0
    except (DatasetError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
