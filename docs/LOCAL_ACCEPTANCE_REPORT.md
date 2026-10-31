# Local acceptance report

Date: November 1, 2026 · Asia/Karachi. Target: Think AI Works Project 2, due November 9, 2026.

Status: **PASS — all Phases 0–9 completed locally.** Final setup, service readiness, current-code tests,
live browser acceptance, data-isolation and secret checks completed successfully.

## Operating model and data isolation

Local single-user React/FastAPI/worker application; no accounts, organization permissions, remote hosting or real email delivery. Ordinary application tables start empty.

Database/API tests use unique schemas inside rolled-back transactions. Browser acceptance uses a committed disposable schema so independent API/worker/browser processes can verify reload persistence. The harness stops its services and drops only its generated schema. Synthetic contacts/sender context are explicitly labeled test fixtures and never inserted into ordinary application data. The real research company is the Python Software Foundation, using its public website.

## Real integrations observed

- Existing pooled/direct Neon connections worked; Alembic revision `0001_core` is applied.
- PostgreSQL vector extension 0.8.6; ten application tables plus Alembic version metadata.
- Public source fetching succeeded with verified TLS and pinned public-IP destinations.
- Actual `gemini-3.5-flash-lite` research selected stored evidence passages; saved findings contain server-attached verbatim quotes and checked source references.
- Actual `gemini-embedding-001` vectors had 768 dimensions and were stored in pgvector. Cosine search returned attributed, company-scoped passages; unrelated-company queries did not leak those passages.
- Real Gemini generated distinct drafts for distinct research contexts. Edits/regeneration preserved historical versions.
- Approval events refer to exact versions. Editing approval resets it; rejection notes, explicit reopening and archive restrictions are persisted.
- Approved JSON export reports `delivery_status: not_sent`. No mail-sending transport or endpoint exists.

The original configured Flash alias exhausted its 20/day free quota. The user authorized Flash-Lite; an ignored `.env.local` selects it while original `.env` remains unchanged. Google documents a free tier; the project's exact 500/day allowance was not independently accessible through the public API/docs and is not claimed as verified.

## Required acceptance sequence and evidence

| # | Check | Executed evidence |
| --- | --- | --- |
| 1 | Start backend/frontend/worker | PowerShell launcher executed with HTTP/process readiness checks |
| 2 | Neon connectivity | Live pooled/direct checks and database status API |
| 3 | Migrations applied | Alembic upgrade/current and schema/vector introspection |
| 4 | Create company/prospect | Isolated browser CRUD and full real-workflow API |
| 5 | Refresh persistence | Browser reload retained created prospect |
| 6 | Valid CSV import | Browser uploaded and confirmed two controlled rows |
| 7 | Deduplication/totals | One imported, one duplicate; row/size/header failures separately tested |
| 8 | Public company research | Live Python Software Foundation source retrieved |
| 9 | Evidence inspection | Browser expanded stored evidence; actual source URL retained |
| 10 | Embeddings | Provider vectors generated/stored; dimension 768 checked |
| 11 | Semantic retrieval | Real query returned company evidence with cosine scores |
| 12 | Gemini draft | Actual model generated a persisted draft |
| 13 | Grounded personalization | Selected research passages and checked quote provenance in saved versions |
| 14 | Edit/save | Browser saved human-edited body as version 2 |
| 15 | Regenerate | Real Gemini created version 3; version 1 remained unchanged |
| 16 | Pending review | New/edited/regenerated versions enter pending |
| 17 | Approve | Browser approved version 3 |
| 18 | Reject another | Edit produced version 4; rejected with reviewer note |
| 19 | Audit history | Explicit reopen created version 5; decision/version/note history retained |
| 20 | Live metrics/charts | Dashboard showed 2 persisted prospects, 0 pending and 1 currently approved draft; generated/review events reflected real actions |
| 21 | Reload whole app | Dashboard reload retained counts |
| 22 | Records remain | Prospect, research and draft history reload checks passed |
| 23 | No email sent | No sending integration; export explicitly marked not_sent |
| 24 | Secrets untracked | Ignore and credential scans; .env/.env.local excluded |
| 25 | Final tests/builds | Final current-code runs passed; results below |

## Automated verification

Phase 8 completed a 34-test backend run, updated research checks (4 passed), updated unit checks (22 passed), five frontend tests, build/lint/format checks and zero-vulnerability npm audits.

Final Phase 9 execution:

| Verification | Observed result |
| --- | --- |
| setup-local.ps1 | Passed: locked Python dependencies, editable package and clean npm ci |
| start-local.ps1 / stop-local.ps1 | Passed: three hidden services, readiness checks and scoped shutdown |
| Complete pytest with RUN_LIVE_TESTS=1 | **35 passed in 178.24 seconds**, actual Neon/public fetch/Gemini/embeddings included |
| Fast script backend unit run | **22 passed**, 13 integration tests intentionally excluded |
| Vitest / Testing Library | **5 passed** |
| TypeScript + production Vite build | Passed, no size warning; main 334 kB, largest route 419 kB |
| Ruff / format / ESLint / pip check | Passed |
| npm audit | **0 vulnerabilities** in complete and production-only audits; clean reinstall also audited 0 |
| Normal Playwright suite | **3 passed**, 3 isolated-only cases intentionally skipped |
| Final real browser workflow | **1 passed in 1.4 minutes**, all business steps and zero console/resource errors |
| Migration | **0001_core (head)**; vector 0.8.6; frozen DDL reproduction separately passed |
| Data isolation | No remaining generated test schemas; all ten ordinary application tables have 0 records |
| Secret tracking | .env and .env.local ignored/untracked; configured credential scans passed |

Original .env is still 559 bytes with its pre-development modification time of October 31, 2026,
23:33:28 PKT. Backend, frontend and worker are running locally. Final screenshots were inspected,
including actual isolated workflow data and the genuine empty ordinary workspace.

Browser cases:
- Normal navigation/CSV preview/keyboard/mobile/empty dashboard checks: 3 passed in Phase 8.
- Isolated prospect create/reload/edit/detail/delete: passed.
- Isolated populated dashboard/range/reload: passed.
- Expanded real CSV/research/embedding/outreach/version/review/export/activity/dashboard workflow: passed with zero browser console/resource errors.
- Three isolated-only tests are intentionally skipped by the normal browser command; they run through the separate schema harness.

## Local commit history

| Phase | Commit | Result |
| --- | --- | --- |
| 0 | `6b3a223` | Foundation |
| 1 | `04c1df9` | Neon schema/backend |
| 2 | `4f95c00` | Prospect management/ingestion |
| 3 | `f9bf18c` | Grounded research |
| 4 | `145cd29` | Embeddings/retrieval |
| 5 | `6b60323` | Outreach/versioning |
| 6 | `0e4e64d` | Human approval |
| 7 | `653a57e` | Live analytics/red dashboard |
| 8 | `0a6aa5d` | Hardening/end-to-end verification |
| 9 | Pending acceptance completion | Final local release/documentation |

No Git remote was contacted, push/PR created, CI configured or deployment attempted.

## Known limitations

- Local single-user MVP; one worker, internet access and usable provider quota are required.
- Public supplied-URL discovery and explicit structured directory metadata; no broad search provider, authenticated scraping or contact harvesting.
- Fixed 768-dimensional migration; exact scans suit the current small dataset. Future growth may justify HNSW.
- Quotes establish source provenance rather than independent truth; summaries and claims still need human review.
- Provider/site availability and quotas can change. Failed jobs retain honest status and can be explicitly rerun.
- Approved messages are drafts only; delivery, replies, deals and revenue are outside scope.

Startup/testing/migration commands and later GitHub synchronization instructions are in the root README. Screenshots and service logs are local ignored artifacts.
