# Threat Model

## Scope

This model covers the local CLI, optional development API, versioned datasets, and generated benchmark artifacts. It does not claim to secure an LLM, a vector database, or a production RAG application.

## Assets and trust boundaries

Important assets are evaluation integrity, corpus confidentiality, benchmark artifacts, developer machines, and CI credentials. Corpus records and queries are untrusted inputs. The optional HTTP boundary is also untrusted. The process filesystem and CI runner are trusted only to the degree provided by their operators.

| Threat | Example impact | Existing control | Production follow-up |
|---|---|---|---|
| Evaluation poisoning | A contributor edits relevance judgments to make a weak retriever appear better | Versioned data, code review, SHA-256 fingerprints, per-query evidence | Signed dataset releases and independent label review |
| Sensitive-data leakage | Customer text is added to fixtures or artifacts | Synthetic bundled data, contributor guidance, no request payload logging | DLP scanning, retention controls, encrypted experiment storage |
| Resource exhaustion | Very large JSONL or long HTTP queries consume memory or CPU | API query length and `k` limits | File-size limits, streaming ingestion, gateway timeouts and quotas |
| Path misuse | An operator points the CLI at unintended local files | Explicit paths and read-only loading | Sandboxed worker and allowlisted dataset registry |
| Indirect prompt injection | Retrieved text contains instructions intended for a later LLM | Retriever treats text as data and never executes it | Instruction/data separation, tool authorization, adversarial tests |
| Cross-tenant retrieval | A shared corpus returns another tenant's document | Not addressed by this single-user baseline | Mandatory tenant filter before ranking plus authorization tests |
| Artifact tampering | A passing result is replaced after evaluation | Atomic writes and input hashes | Signed artifacts, immutable storage, protected CI provenance |
| Dependency compromise | Optional API package or CI action is compromised | Dependency-free core, minimal extras, read-only CI token | Lock files, hash verification, pinned action SHAs, dependency scanning |
| Unauthenticated API | A remotely bound development server exposes corpus content | Docker image contains only synthetic data; docs default to localhost | Authentication, TLS, gateway limits, authorization, audit records |

## Abuse cases to test before production

1. Documents containing instruction-like strings, HTML, scripts, and misleading citations.
2. Unicode confusables, extremely repetitive terms, blank queries, and oversized records.
3. Relevance labels that reference missing, duplicated, or cross-tenant documents.
4. Retrieval queries designed to enumerate confidential corpus contents.
5. Modified threshold files that silently lower release requirements.

## Residual risk

Lexical groundedness is not entailment. A high overlap score can still support a false, contradictory, or unsafe answer. BM25 scores are not calibrated confidence values. The API has no authentication and is intended for local demonstration only.
