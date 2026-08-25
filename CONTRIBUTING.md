# Contributing

Thank you for improving the workbench. Small, reviewable changes with benchmark evidence are preferred.

## Development workflow

1. Create a Python 3.11 or newer virtual environment.
2. Run `make install`.
3. Add or update tests for behavior changes.
4. Run `make test validate benchmark`.
5. Explain metric changes in the pull request. If a threshold changes, include evidence that the new value reflects an intentional product decision rather than hiding a regression.

## Dataset changes

Never put private, customer, proprietary, or production text into this repository. Add a new versioned folder under `data/` for breaking evaluation changes. Keep prior versions when longitudinal comparison matters. Every query needs at least one relevant document and a concise reference answer.

## Code expectations

- Keep the core dependency-free and deterministic.
- Prefer typed, documented functions with explicit failure modes.
- Treat artifact schema changes as versioned interfaces.
- Avoid network access in unit tests.
- Do not weaken a regression gate simply to make CI pass.

By contributing, you agree that your contribution is licensed under the MIT License.
