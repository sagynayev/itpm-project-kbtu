# PDD ChatBot

AI assistant for learning Kazakhstan traffic rules. The product answers a learner's question in three layers: a short answer, a plain-language explanation, and a link to the exact official clause. The MVP must refuse to improvise when no reliable source is found.

**Project planning baseline:** 29 October 2026. **Repository implementation published:** 5 November 2026.

This repository turns the TSIS 4-7 project documents into an implementation. The current code covers the Sprint 1 foundation:

- registration and token login;
- storage and idempotent import of cleaned PDD clauses;
- deterministic clause retrieval;
- a documented JSON answer-service boundary;
- a three-layer extractive fallback that never invents a rule;
- question history and a React chat skeleton;
- backend tests and GitHub Actions CI.

The LLM and hallucination classifier are deliberately not hard-coded into the web layer. Alimzhan can replace the fallback behind the same answer-service interface during Sprint 2.

## Team

| Member | Main responsibility |
|---|---|
| Nurdos | PM / Product Owner, UI/UX, QA and scope control |
| Alikhan | Django backend, database, authentication and React UI |
| Alimzhan | PDD cleaning, retrieval, LLM/RAG, guardrail and evaluation |

## Run the backend

Requires Python 3.12+.

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
py manage.py migrate
py manage.py runserver
```

By default development uses SQLite. Set the `POSTGRES_*` variables from `.env.example` to use PostgreSQL.

Import a cleaned JSONL file:

```powershell
py manage.py import_pdd ..\data\pdd_articles.jsonl --report ..\data\import-report.json
```

Each JSONL row must match [the data contract](docs/pdd-data-contract.md). Only a currently valid official source should be imported; the repository intentionally contains no invented legal clauses.

## Run the frontend

Requires Node.js 20+.

```powershell
cd frontend
npm install
npm run dev
```

The app opens at `http://localhost:5173` and expects the API at `http://localhost:8000/api`.

## Test

```powershell
cd backend
py manage.py test
```

## Project documents

- [TSIS 4-7 implementation map](docs/TSIS-4-7-summary-ru.md)
- [Answer-service interface](docs/answer-service-interface.md)
- [Official PDD data contract](docs/pdd-data-contract.md)
- [Definition of Done](docs/definition-of-done.md)

## Current boundary

The current retrieval algorithm is a transparent baseline, not the final RAG model. It returns an official stored clause only when token overlap is high enough; otherwise it returns `no_source`. Sprint 2 should add embeddings/LLM generation, the configurable guardrail, regeneration (maximum two attempts), fallback to the official text, logging, and evaluation on at least 100 labeled answers.

