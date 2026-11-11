<h1 align="center">
  <img src="frontend/public/favicon.svg" alt="Outbound SDR Agent logo" width="80" height="80" />
  <br />
  Outbound SDR Agent
</h1>

<p align="center">
  <img src="https://img.shields.io/badge/React-20232A?style=flat-square&amp;logo=react&amp;logoColor=61DAFB" alt="React" />
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&amp;logo=typescript&amp;logoColor=white" alt="TypeScript" />
  <img src="https://img.shields.io/badge/Vite-646CFF?style=flat-square&amp;logo=vite&amp;logoColor=white" alt="Vite" />
  <img src="https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=flat-square&amp;logo=tailwindcss&amp;logoColor=white" alt="Tailwind CSS" />
  <br />
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&amp;logo=python&amp;logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&amp;logo=fastapi&amp;logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&amp;logo=postgresql&amp;logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/Gemini-8E75B2?style=flat-square&amp;logo=googlegemini&amp;logoColor=white" alt="Gemini" />
</p>

<p align="center">
  A single-user outbound SDR workspace for <strong>Think AI Works</strong>.<br />
  Research prospects, generate evidence-based outreach, and review every draft before export.
</p>

## Features

- Manage companies and contacts with search, filters, qualification, and do-not-contact controls.
- Import CSV lists with column mapping, validation, duplicate detection, and a reviewable preview.
- Discover companies from public source URLs and confirm candidates before importing them.
- Research companies with Gemini, inspect citations, and distinguish facts from AI hypotheses.
- Search company evidence with Gemini embeddings and PostgreSQL pgvector retrieval.
- Generate personalized outreach in three tones using your sender details and offer.
- Edit and regenerate drafts with immutable versions, reviewer notes, and approval history.
- Approve, reject, archive, or reopen drafts; copy or export approved versions as JSON.
- Track research, outreach activity, and review decisions through a responsive dark dashboard.

**Approved outreach remains a draft. Email sending is disabled.**

## Technology

| Component             | Technology                                                      |
| --------------------- | --------------------------------------------------------------- |
| Frontend              | React, TypeScript, Vite, Tailwind CSS, TanStack Query, Recharts |
| UI and forms          | Radix/shadcn primitives, React Hook Form, Zod, Lucide           |
| Backend               | FastAPI, Pydantic, SQLAlchemy, Alembic                          |
| Database              | Neon PostgreSQL, JSONB, pgvector                                |
| Research and outreach | Google Gemini, Google GenAI SDK, LangChain Runnable stages      |
| Background processing | PostgreSQL-backed queue and a local Python worker               |
| Testing               | pytest, Ruff, Vitest, Testing Library, Playwright               |

## Getting started

**Requirements:** Windows PowerShell, Python 3.11+, Node.js 22.12+, npm, a Neon PostgreSQL database, and a Gemini API key. Browser tests use Microsoft Edge.

Clone the repository:

```powershell
git clone https://github.com/ushalabs/Outbound-SDR.git
cd Outbound-SDR
```

For a new checkout, copy `.env.example` to `.env` and configure the backend:

```powershell
Copy-Item .env.example .env
```

| Variable                    | Purpose                                                      |
| --------------------------- | ------------------------------------------------------------ |
| `DATABASE_URL`              | Pooled Neon PostgreSQL runtime connection with SSL           |
| `DIRECT_DATABASE_URL`       | Direct, non-pooler connection for migrations                 |
| `GEMINI_API_KEY`            | Gemini research, generation, and embedding credentials       |
| `GEMINI_MODEL`              | A structured-generation model available to your project      |
| `EMBEDDING_MODEL`           | An available embedding model, such as `gemini-embedding-001` |
| `EMBEDDING_DIMENSIONS`      | Keep `768` for the current schema                            |
| `APP_ENV`                   | Use `development` for local operation                        |
| `ENABLE_REAL_EMAIL_SENDING` | Keep `false`                                                 |

Credentials stay in the backend environment. `.env`, `.env.local`, dependencies, logs, and runtime artifacts are excluded from Git. Optional `.env.local` values override `.env`; process environment variables take precedence. Model availability and quotas depend on your Gemini project.

Install dependencies and start the application:

```powershell
.\scripts\setup-local.ps1
.\scripts\start-local.ps1
```

The launcher applies migrations, starts the frontend, backend, and research worker, and verifies readiness. No Docker is required.

| Service           | Local URL                          |
| ----------------- | ---------------------------------- |
| Application       | <http://127.0.0.1:5173>            |
| API documentation | <http://127.0.0.1:8000/docs>       |
| Health check      | <http://127.0.0.1:8000/api/health> |

Stop the services with:

```powershell
.\scripts\stop-local.ps1
```

See [setup and operations](docs/SETUP.md) for manual service commands, database migrations, troubleshooting, and all environment variables.

## Security and data handling

Provider keys and database credentials remain server-side. The frontend calls the local API, which uses Neon PostgreSQL with TLS. Public company text and supplied business context are sent to Gemini for the corresponding research and drafting requests.

Public-source fetching checks destination addresses, TLS, robots policies, redirects, size, and time limits. Citations point to stored evidence; AI hypotheses remain labeled. Every edit or regeneration creates a new version requiring review. Do-not-contact prospects are blocked from generation, approval, and export.

The application is designed for one trusted user on localhost. It has no account or organization authentication and no email delivery integration. Approved exports identify the exact version and retain `delivery_status: not_sent`.

## Testing

Run the local verification script after installing dependencies:

```powershell
.\scripts\test-local.ps1
```

Frontend checks can also run separately:

```powershell
cd frontend
npm test
npm run build
npm run lint
npm run test:e2e
```

The normal browser suite expects the app running with an empty workspace. Isolated persistence and live AI acceptance tests use disposable database schemas. Live checks use actual services and consume Gemini quota; they do not send emails. See [testing commands](docs/SETUP.md#tests-and-builds) and the [acceptance report](docs/LOCAL_ACCEPTANCE_REPORT.md).

## Documentation

| Guide                                                | Contents                                                                            |
| ---------------------------------------------------- | ----------------------------------------------------------------------------------- |
| [Setup and operations](docs/SETUP.md)                | Installation, configuration, architecture, migrations, testing, and troubleshooting |
| [Assignment](docs/ASSIGNMENT.md)                     | Original project requirements                                                       |
| [Phase reports](docs/PHASE_REPORTS.md)               | Implementation stages, validation, and development history                          |
| [Acceptance report](docs/LOCAL_ACCEPTANCE_REPORT.md) | Original release verification and operational limits                                |
| [Frontend changes](frontend/UNSLOP.md)               | Dashboard design direction and frontend verification                                |
