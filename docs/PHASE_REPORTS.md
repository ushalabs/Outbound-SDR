# Phase reports

Phases are gated by executed verification. No application seed data is installed.
The supplied dashboard image is the visual reference; its geometry will be adapted to red.
Commit hashes are recorded in the next phase's log entry, since a commit cannot include its own hash.

## Phase 0 — PASS

Implemented: secret-safe settings with existing environment aliases, structured redacted logging,
FastAPI health API and CORS, initial backend tests; React/Vite/TypeScript, Tailwind,
shadcn-style owned Button, React Router shell, TanStack Query, typed API client and shared states.

Tests executed: pytest (4 passed), Ruff (passed), pip check (passed), TypeScript and Vite
production build (passed), Vitest (3 passed), ESLint (passed), npm audit (0 vulnerabilities),
Playwright/installed Edge (1 passed: live health, six routes, no browser page errors).
The actual PowerShell launcher started both services. Screenshot: ignored `artifacts/phase-0-desktop.png`.
Source includes backend/app, backend/tests, frontend/src, frontend/tests/e2e, scripts, root ignore/config docs.
Database changes: none. No seed data or static metrics. Secret scan is run before committing.
Local Git commit: `phase-0: initialize local application foundation` (hash recorded in the next entry).
Known limitations: database and AI verification belong to subsequent phases; workspaces currently
describe the foundation state. Frontend toolchain upgraded to Vite 8, Vitest 5 and ESLint 10;
minimatch 11 override removes the audited transitive denial-of-service vulnerability.
Next phase: Phase 1, Neon schema and backend persistence.

## Phase 1 — PASS

Phase 0 commit: `6b3a223`.
Backend: SQLAlchemy models and pooled engine; direct-connection Alembic; sanitized database errors;
live `/api/system/database` status. Frontend: typed company/prospect/research/draft/version/event
interfaces, live Neon status using TanStack Query and API error state.
Database: migration `0001_core` creates 11 application tables under `sdr`, UUID keys, JSONB,
vector(768), foreign keys, unique/status constraints and lookup/time indexes. `vector` extension installed.
Before migration, both connections succeeded and the existing database had no application tables.
No unrelated tables were modified. No ordinary application records were inserted.
Tests executed: all 6 pytest tests passed, including 2 live Neon tests; create/read, unique constraint,
foreign key, status constraint and vector dimensions verified. Test schema DDL/data rolled back;
test verified its schema no longer exists. Ruff passed after fixing imports/typed dependencies.
Frontend build and lint passed; live browser navigation/Neon status check passed (1 Playwright test).
Migration ran successfully twice (second run idempotent through Alembic).
Local Git commit: `phase-1: implement neon database and core backend` (hash follows next entry).
Limitations: 768 dimensions are frozen in the initial schema; another dimension requires a new migration.
No vector index is needed for an empty dataset; retrieval/index policy belongs to Phase 4.
Automatic destructive downgrades are disabled. Next: Phase 2, prospect management and ingestion.

## Phase 2 — PASS

Phase 1 commit: `04c1df9`.
Backend: complete prospect create/read/update/confirmed delete, searchable/filtered/sorted/paged lists,
bulk qualification and do-not-contact, company/contact detail, validated CSV mapping/preview/import,
row errors, duplicate detection, import jobs and activity records. Imports use savepoints within one
transaction. File limit 2 MB / 1,000 rows. Public-URL company discovery has confirmation before import;
it never invents contact data. A page title is explicitly labeled as a name suggestion for user confirmation.
Fetcher checks robots, public addresses, pinned DNS destinations, redirect policies, TLS, response type,
size and time limits. Discovery has bounded URL counts and per-minute request limits.
Frontend: full Prospects table, search/filter/sort/pagination, selection/bulk actions, add/edit dialogs,
confirmed deletion, company details, CSV mapping/preview/results, discovery/evidence preview,
source links and research/outreach navigation. Responsive screenshots visually inspected.
Database changes: no schema migration; writes use existing companies/prospects/import/activity tables.
Tests: initial full pytest run had 15 passed / 1 TLS failure. Fixed by using certifi's CA bundle with
certificate verification enabled. Rerun of all 10 prospect/fetch tests passed including live public
example.com evidence and isolated real Neon CRUD/import/deduplication. Earlier 6 foundation/database
tests also passed. Vitest 3 passed, build and lint passed, Ruff passed. Normal browser suite: 2 passed.
Separate isolated Neon browser harness: 1 passed, covering create, reload persistence, edit, company
detail and confirmed deletion. Its dedicated schema was dropped after server shutdown; normal
application data stayed empty. No synthetic fixtures were committed to ordinary application tables.
Final full regression: 16 pytest tests passed including live Neon and public fetch; Ruff passed.
Normal browser rerun: 2 passed, 1 intentionally skipped (the isolated persistence test, separately passed
through its harness). Final mobile empty-state screenshot also inspected after loading completed.
Local Git commit uses the required Phase 2 message; hash follows next entry.
Known limitations: public-URL discovery only, no broad web search provider; no authenticated-site scraping.
Research/outreach row actions lead to subsequent-phase workspaces. Next: Phase 3, grounded Gemini research.

## Phase 3 — PASS

Phase 2 commit: `4f95c00`.
Backend: durable queued/running/completed/failed research jobs; separate local worker claims jobs with
row locks, marks interrupted runs failed after 10 minutes, retains evidence/history and supports explicit
reruns. Public evidence retrieval and explicitly labeled manual notes feed LangChain Runnable stages:
retrieve, Gemini structured analysis, citation validation. Every source reference and quotation is checked
against stored evidence. Hypotheses and missing information are separate from supported statements.
Frontend: prospect search/selection, queue/start, real stage polling, reruns, history, detailed intelligence,
quote citations, evidence inspector, hypothesis panels and outreach navigation.
Database: existing research/source/chunk/activity tables; no schema migration. Research and chunk text
persist, no embeddings are claimed yet. Successful reruns invalidate previous company vectors.
Tests: 3 research pytest tests passed (citation rejection, durable provider failure/rerun, real public
Python Software Foundation retrieval + Gemini + Neon persistence). Ruff, build and ESLint passed.
Isolated browser/worker E2E: 1 passed (46.6 seconds), including real queued processing, source evidence,
reload and historical results. Its dedicated schema was removed afterward. Screenshot visually inspected.
Provider access: configured `gemini-3.5-flash` is available; structured connectivity check passed after
a transient 503. Full schema initially returned 400; simplified provider decoder constraints fixed this,
while all local Pydantic limits and source-quote checks remain enforced. No model/key was replaced.
Available embedding models were listed by the live provider API.
Local Git commit uses required Phase 3 message; hash follows next entry.
Limitations: source citations establish textual provenance, not independent verification of website claims;
AI summaries/qualification still require human review. Worker must be running. No browser/site auth bypass.
Next: Phase 4, real embeddings and company-scoped semantic retrieval.

## Phase 4 — PASS

Phase 3 commit: `f9bf18c`.
Backend: live Google embedding model capability check, real normalized 768-dimensional embeddings,
finite/count/dimension validation, pgvector cosine retrieval with current-research and company scope,
source attribution, model/state tracking and explicit failed re-embedding state (old vectors cleared).
The existing environment has no EMBEDDING_MODEL, so the application selects `gemini-embedding-001`,
which was returned by the provider model list. `.env` is unchanged.
Frontend: embedding status/action and semantic passage search within research detail.
Database: existing vector column used; no schema changes. Dataset is small, so exact cosine scanning
is the appropriate policy. HNSW should be considered when current chunk count exceeds 1,000.
Tests so far: real embedding + scoped semantic retrieval + source attribution + failure-clears-vector
test passed against isolated Neon; returned dimension was 768. Build, lint and Ruff passed.
SQLAlchemy 2.1 emits a non-failing DISTINCT ON deprecation warning; current <3 dependency supports it.
Browser acceptance with real public website, Gemini research, live embeddings and pgvector retrieval
passed (1 browser test, 50.8 seconds). Evidence and cosine similarity appeared in the frontend;
the dedicated test schema was removed. No simulated success was used.
Local Git commit uses required Phase 4 message; hash follows next entry. Next: Phase 5, outreach drafting.
