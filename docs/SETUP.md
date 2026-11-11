# Outbound SDR Agent · Think AI Works

A local single-user workspace for prospect management, grounded company research, semantic evidence retrieval, personalized outreach and human review. **Approved messages remain drafts; the application does not send email.**

The dark dashboard loads metrics, charts and activity from PostgreSQL. Empty databases show honest zero states. There are no normal seed contacts, mock AI successes, fabricated revenue or pretend reply analytics.

## Features

- Prospect/company CRUD, search, filtering, sorting, pagination, bulk qualification and do-not-contact flags.
- CSV mapping, preview, row errors, duplicate detection and persisted import summaries; 2 MB / 1,000-row limits.
- Confirmed company discovery from up to three public URLs. Structured directory organization metadata is supported, capped at 20 candidates. No people, emails or phone numbers are harvested.
- Durable queued research, local worker, reruns, stored sources, supported statements, labeled hypotheses, qualification and missing-information indicators.
- Real 768-dimensional Gemini embeddings in pgvector and company-scoped cosine retrieval with provenance.
- Three outreach tones, required sender context, subject/body editing, immutable versions and regeneration.
- Pending/approved/rejected/archived review, notes, exact-version audit events, explicit reopening, approved-only copy/JSON export and opt-out guards.
- Live date-filtered dashboard: prospects, coverage, qualification, generation/decision trends, status/industry distributions, turnaround and recent activity.

## Stack and architecture

| Layer          | Implementation                                                                                                                                     |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Frontend       | React 19, TypeScript, Vite 8, Tailwind 4, owned shadcn/Radix primitives, React Router, TanStack Query, React Hook Form/Zod, Recharts, Lucide       |
| API and worker | Python 3.11+, FastAPI, Pydantic v2/settings, SQLAlchemy 2.x, Alembic, psycopg 3, httpx, BeautifulSoup, Google GenAI SDK, LangChain Runnable stages |
| Database       | Neon PostgreSQL, UUID/FK/unique/status constraints, JSONB, pgvector(768), lookup/time indexes                                                      |
| Verification   | pytest/Ruff, Vitest/Testing Library, TypeScript/ESLint, Playwright with installed Edge                                                             |

The browser calls local FastAPI. Runtime SQL uses the pooled Neon URL; Alembic uses the direct URL. PostgreSQL queues research for one local worker. The worker fetches permitted sources, runs structured Gemini analysis, validates evidence selections and persists results. Draft generation retrieves current company evidence before calling Gemini, then saves a new immutable version. Review decisions refer to exact version UUIDs.

## Directory structure

```text
backend/app/           settings, models, routes, services, worker
backend/migrations/    frozen additive application DDL
backend/tests/         unit and isolated live integration checks
backend/scripts/       isolated browser acceptance harness
frontend/src/          workspace pages, shared primitives and typed API client
frontend/tests/e2e/    normal read-only and isolated real-service browser checks
scripts/               setup, start, stop, tests and credential scan
docs/                  assignment, reference image, phase and acceptance reports
artifacts/             ignored logs, process IDs and screenshots
```

## Local installation

Requirements: Windows PowerShell, Python 3.11+, Node.js 22.12+, npm, Microsoft Edge for browser tests, and the private root environment file. Verified with Python 3.13.7 and Node 24.12.0. No Docker is required.

Keep the existing `.env`. For a new checkout, copy `.env.example` to `.env` and replace credential/model placeholders. From the project root:

```powershell
.\scripts\setup-local.ps1
.\scripts\start-local.ps1
```

Open [the workspace](http://127.0.0.1:5173) and [API documentation](http://127.0.0.1:8000/docs). The launcher applies migrations, starts backend/frontend/worker hidden, verifies HTTP/process readiness and records PIDs under ignored `artifacts/`.

```powershell
.\scripts\stop-local.ps1
```

The stop script verifies that each recorded process command line belongs to this checkout. Stop services before reinstalling dependencies. Setup uses `backend/requirements.lock.txt` and `npm ci`.

## Configuration

Python loads `.env`, then optional ignored `.env.local`; process environment variables take precedence. Vite receives no database/provider credentials.

| Variable                                            | Purpose                                                                |
| --------------------------------------------------- | ---------------------------------------------------------------------- |
| `DATABASE_URL`                                      | Existing pooled Neon runtime connection, with SSL                      |
| `DIRECT_DATABASE_URL`                               | Direct non-pooler connection for migrations                            |
| `GEMINI_API_KEY`                                    | Server-side Google credential                                          |
| `GEMINI_MODEL`                                      | Available structured-generation model                                  |
| `EMBEDDING_MODEL`                                   | Optional; defaults to verified `gemini-embedding-001`                  |
| `EMBEDDING_DIMENSIONS`                              | 768 for this migration                                                 |
| `APP_ENV` / `ENVIRONMENT`                           | Environment name                                                       |
| `DEMO_MODE`                                         | Compatibility setting; never seeds records or fakes provider responses |
| `ENABLE_REAL_EMAIL_SENDING` / `ENABLE_REAL_SENDING` | Must be false; true fails validation                                   |

The local override selects `gemini-3.5-flash-lite`, verified with the existing key after user authorization. Original `.env` was preserved. For a new checkout, configure that available free-tier model privately. Google lists free input/output; exact active quotas are project-specific, so 500 RPD is not independently guaranteed. See [pricing](https://ai.google.dev/gemini-api/docs/pricing#gemini-3.5-flash-lite) and [rate limits](https://ai.google.dev/gemini-api/docs/rate-limits).

## Neon and schema

Use the supplied existing database. Alembic creates the isolated `sdr` schema and enables `vector`; unrelated tables are untouched.

Ten application tables: `companies`, `prospects`, `research`, `research_sources`, `research_chunks`, `outreach_drafts`, `draft_versions`, `approval_events`, `activity_logs`, `import_jobs`. Alembic tracks revisions separately in `sdr.alembic_version`.

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m alembic upgrade head
..\.venv\Scripts\python.exe -m alembic current
..\.venv\Scripts\python.exe -m app.check_database
```

Changing vector dimensions requires a new reviewed migration. Exact cosine scans suit the current small dataset; consider HNSW after roughly 1,000 current chunks. Automatic destructive downgrades are disabled.

## Separate service commands

Run these in separate terminals from the project root:

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

```powershell
Set-Location frontend
npm run dev
```

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m app.worker
```

Use one worker per workspace. Queued jobs persist while stopped. Running jobs interrupted beyond the 10-minute recovery window become failed and require explicit rerun.

## Tests and builds

Fast verification without AI quota usage:

```powershell
.\scripts\test-local.ps1
```

All backend tests, including actual Neon, public sources, Gemini and embeddings:

```powershell
Set-Location backend
$env:RUN_LIVE_TESTS = '1'
..\.venv\Scripts\python.exe -m pytest -q
Remove-Item Env:RUN_LIVE_TESTS
```

Tests use unique rolled-back schemas. Migration reproduction also rolls back its separate schema. Live checks consume provider quota.

Full real browser acceptance (CSV through research/vector/outreach/review/export/dashboard):

```powershell
Set-Location backend
..\.venv\Scripts\python.exe scripts\run_browser_acceptance.py tests/e2e/research-live.spec.ts
```

Other isolated checks, one file per invocation:

```powershell
..\.venv\Scripts\python.exe scripts\run_browser_acceptance.py tests/e2e/prospects-persistence.spec.ts
..\.venv\Scripts\python.exe scripts\run_browser_acceptance.py tests/e2e/dashboard-populated.spec.ts
```

Each harness creates a disposable committed schema for cross-process persistence, starts isolated services on 8001/5174, stops them, and drops only its generated schema. Never point cleanup at ordinary application data.

Normal navigation/zero-state browser checks require the ordinary local app running with an empty workspace:

```powershell
Set-Location frontend
npm run test:e2e
```

Isolated-only cases are intentionally skipped in that run. Separate frontend commands: `npm test`, `npm run build`, `npm run lint`. Actual final counts are recorded in [LOCAL_ACCEPTANCE_REPORT.md](docs/LOCAL_ACCEPTANCE_REPORT.md); phase records and commits are in [PHASE_REPORTS.md](docs/PHASE_REPORTS.md).

## Provenance and review safeguards

- The fetcher validates and pins public IP destinations, verifies TLS, checks robots/access policies on redirects and bounds URLs, time, size and frequency. No authentication or restrictions are bypassed.
- Discovery extracts explicit organization metadata. Company names/page-title suggestions require confirmation. Broad web search and contact harvesting are not implemented.
- Research treats external text as untrusted data. Gemini selects stored source/passage IDs; the server attaches exact verbatim citations. Invalid IDs fail after one correction attempt. User notes and hypotheses are labeled.
- Embedding count, dimensions and finite values are validated. Retrieval uses latest completed company research and the matching model; reruns invalidate older vectors.
- Sender context is required; drafts cite retrieved evidence. Human edits are marked and need review. Every save/regeneration creates a version and resets approval.
- Decisions identify exact versions. Do-not-contact prospects cannot generate, approve or export outreach. Export JSON reports `delivery_status: not_sent`.
- Credentials remain server-only and ignored. Input errors omit raw values and logs redact configured secrets. No email transport exists.

## Troubleshooting and limits

| Symptom                           | Action                                                                                                             |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Port in use                       | Stop recorded project services; inspect another process before stopping it manually                                |
| Database unavailable              | Check private URLs, SSL/network and direct-connection migrations                                                   |
| Research stays queued             | Start the worker and inspect ignored worker logs                                                                   |
| Interrupted run                   | Recovery marks it failed after ten minutes; explicitly rerun                                                       |
| Gemini HTTP 429                   | Check active model/project quota in AI Studio; retry after reset or choose another authorized available free model |
| Invalid evidence selection        | Inspect sources and rerun; unsupported findings are not saved                                                      |
| Website policy/TLS/access failure | Use a permitted source or explicitly labeled manual notes                                                          |
| Empty semantic search             | Complete current research and generate its embeddings                                                              |
| Export blocked                    | Check current status/version and do-not-contact flag                                                               |
| Browser launch fails              | Install Edge or adapt the Playwright channel to an installed browser                                               |

Local single-user MVP: no accounts, organization permissions, production hosting, automatic web crawl, email delivery, replies, revenue or deals. Quotations establish textual provenance, not independent truth verification; AI summaries and drafts still require human review. Public sites/models/quotas can change. Live research requires the worker and network.
