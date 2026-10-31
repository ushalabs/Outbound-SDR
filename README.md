# Outbound SDR Agent

Local single-user SDR workspace for Think AI Works. **Phases 0–6 are verified.**
Phases 7–9, including the dynamic dashboard and final hardening, are in progress.
See [phase reports](docs/PHASE_REPORTS.md) and the [incomplete acceptance report](docs/LOCAL_ACCEPTANCE_REPORT.md).

Implemented and verified: prospect CRUD/import/discovery, Neon persistence, grounded public-source
Gemini research, pgvector semantic retrieval, personalized outreach drafts and immutable versions.
Approval APIs and interface passed database and live browser acceptance, including versioned decisions,
rejection notes, reopening, export and activity. There is no email-sending integration.

## Local setup

Requirements: Python 3.11+, Node.js 22.12+ (tested with Python 3.13 and Node 24), npm,
PowerShell, and the existing root `.env`. No Docker or email provider is required.

```powershell
.\scripts\setup-local.ps1
.\scripts\start-local.ps1
.\scripts\test-local.ps1
```

Open <http://127.0.0.1:5173>. API documentation: <http://127.0.0.1:8000/docs>.
The launcher starts backend, frontend and the research worker as hidden child processes, with ignored
logs/process IDs under `artifacts/`.
Stop services using the displayed PIDs with `Stop-Process -Id <PID>`.

Separate startup commands, from the project root in two terminals:

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

```powershell
Set-Location frontend
npm run dev
```

## Configuration and safeguards

Root `.env` is loaded only by Python. Never put provider credentials in Vite variables.
Optional ignored `.env.local` overrides selected settings. The local model selection is
`gemini-3.5-flash-lite`, verified using the existing key after user authorization; `.env` is unchanged.
`.env.example` contains placeholders. Existing `ENVIRONMENT` and `ENABLE_REAL_SENDING`
names are accepted as aliases. Sending must be false; enabling it fails validation.
`DEMO_MODE` does not insert sample records or substitute API results.
All ordinary workspaces begin empty. Test fixtures remain isolated from application data.

Worker separately, if not using the launcher:

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m app.worker
```

Migrations (uses the direct URL, scoped to `sdr`):

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m alembic upgrade head
```

Tests without AI quota usage:

```powershell
.\scripts\test-local.ps1
```

To run real browser acceptance with available provider quota:

```powershell
Set-Location backend
..\.venv\Scripts\python.exe scripts\run_browser_acceptance.py tests/e2e/research-live.spec.ts
```

This harness creates a dedicated Neon schema, starts isolated services, runs real provider calls and
removes only that schema after stopping its services. Do not repeatedly rerun it on exhausted quota.

## Architecture

- `backend/app`: FastAPI routes, SQLAlchemy models, Pydantic settings, redacted logging and local worker.
- `backend/app/services`: source fetching, LangChain research pipeline, Gemini generation/embeddings,
  pgvector retrieval, versioned outreach and persisted activity.
- `backend/migrations`: frozen, additive initial DDL in a dedicated `sdr` schema.
- `backend/tests`: pytest API and configuration checks.
- `frontend/src`: React, TypeScript, React Router, TanStack Query and Tailwind CSS.
- `frontend/src/components/ui`: owned shadcn/ui component source.
- `frontend/tests/e2e`: Playwright browser verification.
- `scripts`: local PowerShell setup, startup and verification.
- `docs`: assignment, dashboard reference and phase reports.

Runtime queries use the supplied pooled Neon URL; Alembic uses the direct URL. All ordinary application
data is empty by default. Tests use isolated schemas. Decoder schemas are simplified for Gemini, with
full local validation and exact source-quote checks after generation. Hypotheses remain labeled.

Current limitations: public-URL discovery only; 768-dimensional schema; exact vector scans for small
datasets; worker required for queued research; single-user local operation; provider quota limits;
analytics/dashboard and final hardening are pending. Approval means ready for export, never delivery.
