# Outbound SDR Agent

Local single-user SDR workspace for Think AI Works. Built in sequential, verified phases;
see [phase reports](docs/PHASE_REPORTS.md) for the actual implementation status.

## Local setup

Requirements: Python 3.11+, Node.js 22.12+ (tested with Python 3.13 and Node 24), npm,
PowerShell, and the existing root `.env`. No Docker or email provider is required.

```powershell
.\scripts\setup-local.ps1
.\scripts\start-local.ps1
.\scripts\test-local.ps1
```

Open <http://127.0.0.1:5173>. API documentation: <http://127.0.0.1:8000/docs>.
The launcher uses hidden child processes and writes ignored logs/process IDs under `artifacts/`.
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
`.env.example` contains placeholders. Existing `ENVIRONMENT` and `ENABLE_REAL_SENDING`
names are accepted as aliases. Sending must be false; enabling it fails validation.
`DEMO_MODE` does not insert sample records or substitute API results.
All ordinary workspaces begin empty. Test fixtures remain isolated from application data.

## Foundation architecture

- `backend/app`: FastAPI, Pydantic settings and redacted JSON logging.
- `backend/tests`: pytest API and configuration checks.
- `frontend/src`: React, TypeScript, React Router, TanStack Query and Tailwind CSS.
- `frontend/src/components/ui`: owned shadcn/ui component source.
- `frontend/tests/e2e`: Playwright browser verification.
- `scripts`: local PowerShell setup, startup and verification.
- `docs`: assignment, dashboard reference and phase reports.

Database, research, vector search and outreach acceptance are tracked by phase.
No sending integration exists. Approval will mean a draft is ready for export, never delivery.
