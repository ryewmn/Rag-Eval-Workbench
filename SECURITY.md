# Security Policy

## Supported versions

The latest commit on `main` receives security fixes. This project is an educational evaluation tool and is not a hosted multi-tenant service.

## Reporting a vulnerability

Please use GitHub private vulnerability reporting when enabled. Otherwise, contact the repository owner privately. Do not open a public issue containing exploit details, private data, credentials, or unsafe datasets.

Include the affected version, reproduction steps, impact, and any proposed mitigation. You should receive an acknowledgment within five business days.

## Safe operation

- Run only on data you are authorized to process.
- Keep secrets and production documents out of JSONL fixtures and benchmark artifacts.
- Bind the development API to localhost unless access controls and TLS are provided by a trusted gateway.
- Apply request size limits and authentication before exposing the API beyond a local development environment.
- Review `docs/THREAT_MODEL.md` before adapting the project for production.
