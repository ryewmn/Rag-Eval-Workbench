# Model Card: BM25 Retrieval Baseline

## Summary

This project uses Okapi BM25, a deterministic lexical ranking algorithm rather than a trained generative model. It is included as an interpretable baseline for retrieval-augmented generation experiments.

## Intended use

- Reproduce retrieval quality on a small, versioned evaluation set.
- Detect ranking regressions in pull requests.
- Inspect lexical matches before adopting a more complex semantic or hybrid retriever.
- Teach retrieval metrics and ML evaluation discipline.

## Out-of-scope use

- Making safety-critical, legal, medical, credit, employment, or access-control decisions.
- Treating BM25 score as probability, factuality, or answer confidence.
- Evaluating multilingual, image, audio, or large production corpora without new evidence.
- Using the included development API as an internet-facing service.

## Data

The bundled `rag-eval-handbook-mini` dataset is synthetic and hand-authored in English. Version 1.0 contains 12 short documents and 10 queries about ML, retrieval, and AI security. Binary relevance judgments are not independently annotated and therefore demonstrate the workflow rather than establish a scientific benchmark.

## Evaluation

The reference configuration evaluates top-three results with Recall@3, MRR@3, nDCG@3, citation precision, lexical groundedness, and latency percentiles. Dataset hashes and per-query rankings are written to the result artifact.

## Limitations and fairness

BM25 depends on shared vocabulary and can miss semantically related phrasing. Tokenization is English-oriented. The tiny synthetic benchmark has no demographic subgroups and cannot support fairness claims. Citation precision assumes every retrieved context would be cited. Groundedness measures token overlap, not entailment or factual correctness.

## Operational guidance

Create representative judgments for the target domain, review them with domain experts, add adversarial and slice-based evaluations, and compare BM25 with semantic and hybrid candidates. Monitor both quality and latency after deployment. Human review remains necessary for high-impact systems.
