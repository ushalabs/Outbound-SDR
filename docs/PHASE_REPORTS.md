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
Database: migration `0001_core` creates 10 application tables plus the Alembic version table under `sdr`, UUID keys, JSONB,
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

## Phase 5 — PASS

Phase 4 commit: `145cd29`.
Backend: company-scoped semantic evidence retrieval feeds real Gemini outreach generation, with required
sender identity/value proposition, three tones, checked citations, immutable draft versions, editing,
regeneration, optimistic version checks and pending-review defaults. Do-not-contact prospects are blocked.
Frontend: sender context, tone, research readiness, saved drafts, subject/body editor, preview, history,
regeneration and quote provenance. Sender context is retained locally in the browser, never provider keys.
Database: existing outreach/version/approval-event/activity tables used; no schema changes.
Tests so far: real generation with two distinct isolated research contexts passed; citations map to each
source, bodies differ, edits preserve v1, regeneration creates v3, persistence and opt-out checks passed.
Build, ESLint, Vitest (3 passed) and Ruff passed. Browser sequence initially failed because the populated
textarea's implicit label included its contents. Explicit accessible names fixed it; the rerun passed
(1 browser test, 1.7 minutes), covering real research, embeddings, semantic retrieval, generation, editing,
v3 regeneration, v1 immutability and reload persistence. Dedicated schema cleaned afterward.
Email assembly now preserves readable paragraph breaks using validated generated sections and the
supplied sender signature. Source evidence and human-edited status remain visible.
No mail transport, credentials or sending endpoint exists.
Local Git commit uses required Phase 5 message; hash follows next entry. Next: Phase 6, approval workflow.

## Phase 6 — PASS

Phase 5 commit: `6b60323`.
Backend: validated pending/approved/rejected/archived transitions, version-locked decisions, optional
notes, explicit reopen-as-new-version, approved-only JSON export with `delivery_status: not_sent`,
opt-out guards, status counts, search/filter/pagination and persisted activity feed.
Frontend: review queue, live pending badge, version editor, source/research panel, approve/reject/archive
confirmations, regenerate/reopen, notes, immutable audit history, approved copy/export, Activity page.
Review actions are blocked while editing unsaved text or looking at a historical version.
Database: approval events reference exact version UUIDs; no schema changes.
Tests so far: live isolated state-machine/audit/export test passed, covering invalid transitions,
editing resets approval, rejected-note retention, reopening and stale versions. Ruff/build/lint passed.
Build now reports a non-failing chunk-size warning; route splitting will be addressed during hardening.
Full real browser workflow reached valid public research, embeddings and semantic retrieval, then failed
at outreach generation because Gemini returned HTTP 429 RESOURCE_EXHAUSTED. Provider reported:
`generate_content_free_tier_requests`, daily limit 20, resolved model `gemini-3.6-flash` (configured alias
is `gemini-3.5-flash`), retry after approximately 11h19m at the failed request on November 1, 2026 PKT.
The error appeared honestly in the UI. Browser approval/export/activity actions were NOT reached in
this run. The failed test's dedicated schema was removed; normal data was untouched.
No new model, paid tier, key, mock provider or fake success was substituted.
Resume: the user authorized switching to the higher-allowance free Flash-Lite model. Live model listing,
model access and structured generation succeeded for `gemini-3.5-flash-lite`. An ignored `.env.local`
selects it; original `.env` is unchanged. Google documents its free tier; exact project-specific daily
limits are shown in AI Studio, so 500 RPD is not claimed as independently confirmed.
Research gained one bounded citation-correction attempt with the same strict validator. Isolated tests
verified both correction success and rejection after a second invalid result. No unsupported findings save.
The complete live browser workflow then passed (2.3 minutes): source research, embeddings, semantic search,
outreach, editing/regeneration, old versions, approve v3, edit resets approval, reject v4 with note,
reopen v5, approve v5, download approved draft, genuine activity rows. Dedicated schema cleaned afterward.
One earlier run completed all review actions but hit a test selector matching a hidden activity-filter
option; the assertion was scoped to visible event rows. Another run safely rejected an invalid citation;
the bounded correction was added and tested before the final passing run.
Local Git commit uses required Phase 6 message; hash follows next entry. Next: Phase 7 analytics/dashboard.
Final non-AI verification: `scripts/test-local.ps1` passed (13 backend unit tests, 9 integration tests
deselected; Ruff; 3 Vitest tests; TypeScript/production build; ESLint). A 505.85 kB frontend chunk-size
warning remains for Phase 8. The launcher was rerun with current code so Phase 6 is locally reviewable.
Final normal browser suite passed: 2 passed, 2 isolated-only tests intentionally skipped.
Working-tree credential scan passed; `.env` is untracked. Live database status confirms 0 ordinary
companies/prospects and approval counts are all 0. Backend/frontend/worker are running locally.

Resume command from `backend` (requires available Gemini quota; creates/cleans a dedicated test schema):

```powershell
..\.venv\Scripts\python.exe scripts\run_browser_acceptance.py tests/e2e/research-live.spec.ts
```

This command repeats the accepted isolated workflow. Free quota remains limited and complete workflows
consume multiple genuine generation requests.

## Phase 7 — PASS

Phase 6 commit: `0e4e64d`.
Backend: PostgreSQL-derived cohort totals, research coverage, qualification, current draft statuses,
draft generation/decision daily trends, research completion, prospect status and company industry
distributions, recent activity and actual average approval duration. Date ranges use Asia/Karachi,
validate 1–366 days and compare to an equally sized prior period. A zero denominator yields no growth
claim. Empty calendar buckets contain real zero event counts, not synthetic activity.
Frontend: reference-inspired dark sidebar, red hero KPI, shared top analytical panel, upper-right
multi-series draft/decision chart, wide lower-left pipeline chart, review/turnaround cards, status donut,
company industries and persisted recent activity. Working preset/custom ranges, links, tooltips,
loading/error/retry states, honest zero states and responsive layouts.
Database: read-only aggregates over existing indexed tables; no migration.
Tests: isolated Neon analytics test passed, verifying empty data, prospect/research/approval changes,
industry counts, actual daily series, turnaround and date filters. Build and ESLint passed. Normal
empty-dashboard desktop/mobile browser test passed; separate isolated populated-chart/reload/filter
test passed. Screenshots of all three states were inspected. Normal application data stays empty.
Follow-up lint caught loop-variable binding in the Phase 6 correction test fixture; bound its defaults
explicitly and Ruff passed. Recharts callback typing was fixed before the passing build.
Local Git commit uses required Phase 7 message; hash follows next entry.
Known limitations: 924 kB combined frontend bundle warning; route splitting and remaining robustness,
keyboard/contrast review and exhaustive acceptance belong to Phase 8. Next: Phase 8.

## Phase 8 — PASS

Phase 7 commit: `653a57e`.
Backend: shared AI rate limits, cross-origin mutation/Host guards for the local operating model,
transport limits and response headers; CSV headers parsed server-side (quoted commas supported),
one-query preview duplicate lookup, concurrent company creation handling; read endpoints avoid write
locks. Replaced deprecated DISTINCT ON usage with a row-number query. Embedding network/dimension
failures are explicit. Interrupted worker recovery is independently tested. Frozen migration DDL
reproduces exactly the 10 application tables in an isolated rolled-back schema.
Research now asks Gemini to select stored source/passage IDs. The server attaches exact verbatim
passages and validates them; unknown references get one correction attempt, then fail. No AI-invented
quote can become stored evidence. Structured public directory organization metadata yields at most
20 company candidates, with no people/email/phone extraction; unstructured names still need confirmation.
Frontend: lazy routes/shared primitives reduce main JS to 334 kB and largest route to 419 kB, without
the prior size warning. Radix dialogs trap focus/restore it; keyboard checks passed. Improved small-text
size/contrast, disabled chart animations, added favicon and reduced-motion support, formatted owned
source. Historical/unsaved draft review blocks have dedicated UI tests.
Scripts: launcher validates dependencies, checks all three services and local HTTP readiness; added
safe project-command-line-checked stop script. Both were actually executed successfully.
Tests: first full backend run: 33 passed / 1 failed due to the migration test mistakenly counting
Alembic's version table as an application table. Corrected assertion; full rerun: **34 passed**.
After the source-passage change, targeted research tests: **4 passed** (real Gemini/Neon included).
Final current unit suite: **22 passed**, 13 integration tests excluded in that unit-only run.
Frontend: **5 Vitest tests passed**, TypeScript/build/ESLint passed, Ruff/format/pip check passed;
both production-only and complete npm audit report **0 vulnerabilities**.
Normal browser suite: **3 passed**, 3 isolated-only cases intentionally skipped. Isolated prospect
persistence browser test: **1 passed**. Expanded real CSV/research/vector/draft/review/export/dashboard
browser workflow: **1 passed** (1.5 minutes), including reloads and zero console/resource errors.
One preceding end-to-end run completed all business steps but exposed a missing favicon 404; fixed it
and reran successfully. Test schemas were cleaned; normal application data stayed empty.
Local Git commit uses required Phase 8 message; hash follows next entry.
Known limitations: local single-user operation, public URL/structured-directory discovery, provider
quotas, fixed 768-dimensional migration, exact vector scans for the current small dataset, no sending.
Next: Phase 9, repeatable local setup, final acceptance and complete release documentation.

## Phase 9 — PASS

Phase 8 commit: `0a6aa5d`.
Backend/frontend/database: final application is locally functional. No new schema or product features
were added in this phase. Root README now documents features, architecture/stack, all ten tables,
configuration/aliases, private model override, Neon/vector setup, exact commands, worker, tests,
troubleshooting, provenance safeguards, approval-only behavior, limitations and future manual GitHub sync.
`docs/LOCAL_ACCEPTANCE_REPORT.md` maps all 25 required acceptance steps to executed evidence.
Actual setup was rerun: pinned Python dependencies + editable install + clean npm ci passed; npm audit
reported 0 vulnerabilities. Scoped stop and readiness-checked start scripts passed; three services run.
Final full backend command: **35 passed in 178.24 seconds**, including real external services.
Final fast checks: **22 backend unit tests passed**, 13 live tests intentionally excluded; **5 frontend
tests passed**; Ruff/format, ESLint, TypeScript/build and pip check passed. No frontend size warning.
Final normal browser suite: **3 passed**, 3 isolated-only cases intentionally skipped.
Final real isolated CSV → research → embeddings/search → draft/edit/regenerate → approve/reject/reopen
→ export/activity/dashboard → reload workflow: **1 passed in 1.4 minutes**, zero console/resource errors.
Its generated schema was removed. Final catalog checks found no test schemas and zero records in all
ten ordinary application tables. Live Neon reports vector 0.8.6 and Alembic `0001_core (head)`.
Original `.env` remains 559 bytes with its original 2026-10-31 23:33:28 PKT modification time.
Environment files, dependencies and artifacts are ignored/untracked; credential scans passed.
No outbound email, Git remote contact, push/PR, remote CI or deployment occurred.
Local Git commit: required `phase-9: finalize local release and documentation`; its exact hash is
recorded by the subsequent documentation-only audit commit so the phase commit can be identified
without a self-referential hash. Known limitations are listed in the acceptance report and README.
Next phase: none. All ten phase gates passed.
