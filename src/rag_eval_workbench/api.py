"""Optional FastAPI adapter around the same deterministic evaluation core."""

import os
from pathlib import Path
from typing import Any

from .benchmark import run_benchmark
from .io import load_documents
from .retriever import BM25Retriever


def create_app(
    *,
    corpus_path: Path | None = None,
    queries_path: Path | None = None,
    thresholds_path: Path | None = None,
) -> Any:
    """Create an API application. Install the ``api`` extra before calling."""

    try:
        from fastapi import FastAPI, HTTPException
        from pydantic import BaseModel, Field
    except ImportError as exc:
        raise RuntimeError("API dependencies are missing; install with '.[api]'") from exc

    resolved_corpus = corpus_path or Path(os.getenv("RAG_EVAL_CORPUS", "data/v1/corpus.jsonl"))
    resolved_queries = queries_path or Path(os.getenv("RAG_EVAL_QUERIES", "data/v1/queries.jsonl"))
    resolved_thresholds = thresholds_path or Path(
        os.getenv("RAG_EVAL_THRESHOLDS", "config/regression.json")
    )
    retriever = BM25Retriever(load_documents(resolved_corpus))

    class SearchRequest(BaseModel):
        query: str = Field(min_length=1, max_length=2000)
        k: int = Field(default=3, ge=1, le=20)

    app = FastAPI(
        title="RAG Evaluation Workbench",
        version="0.1.0",
        description="Local, deterministic BM25 retrieval and regression evaluation.",
    )

    @app.get("/health")
    def health() -> dict[str, Any]:
        return {"status": "ok", "documents": len(retriever.documents)}

    @app.post("/search")
    def search(request: SearchRequest) -> dict[str, Any]:
        results = retriever.search(request.query, k=request.k)
        if not results:
            raise HTTPException(status_code=422, detail="query must contain searchable tokens")
        return {"query": request.query, "results": [item.to_dict() for item in results]}

    @app.post("/benchmark")
    def benchmark() -> dict[str, Any]:
        return run_benchmark(
            resolved_corpus,
            resolved_queries,
            k=3,
            thresholds_path=resolved_thresholds,
        ).payload

    return app


def application() -> Any:
    """Uvicorn factory entry point that defers file access until startup."""

    return create_app()
