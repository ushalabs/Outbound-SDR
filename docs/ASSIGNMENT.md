# MASTER DEVELOPMENT PROMPT — Think AI Works Project 2: Outbound SDR Agent

## Role and objective

You are the lead full-stack engineer, AI integration engineer, UI engineer, and QA engineer responsible for delivering a complete, locally functional Outbound SDR Agent.

Implement the entire project **phase by phase, from Phase 0 through Phase 9**, with real backend functionality, real database persistence, live AI integrations, a polished frontend, automated tests, and local Git commits.

The attached image is the **mandatory dashboard visual reference**. Preserve its overall layout and card hierarchy, but replace the blue design language with a premium red theme.

This is a functioning internship assignment for Think AI Works, due November 9, 2026.

### Non-negotiable development rules

1. **Local-first development.** GitHub access is not available yet. Do not attempt to push, create PRs, configure remote CI/CD, or deploy.
2. The project root already contains `.env` with Neon and AI credentials. Read existing variable names and use them correctly. Do not overwrite, print, commit, or leak the file.
3. Work sequentially through all 10 phases.
4. After each phase, run its required tests, verify the implementation, and create a distinct local Git commit.
5. Continue automatically to the next phase only after its acceptance gate passes. Do not ask for approval at every phase. Stop for genuine blockers, destructive operations requiring approval, or unavailable credentials.
6. If a phase fails verification, fix it before committing or progressing.
7. All dashboard statistics, charts, research results, prospect records, outreach drafts, and approval history must originate from genuine persisted data or live API results.
8. No fabricated contacts, fictional companies presented as real, mock AI success responses, hardcoded metrics, or pretend analytics.
9. Empty databases must produce genuine empty states, not fake seed records.
10. Tests may use isolated fixtures, mocks, and synthetic data, but they must never appear in normal application data unless explicitly imported as clearly labeled demo data.
11. Fully implement each required feature. Do not leave critical UI buttons, workflows, API endpoints, or modules as TODOs.
12. Prefer simple, maintainable architecture over unnecessary complexity.
13. Use type checking, validation, proper error handling, and real integration tests.
14. Do not silently change the requested technology stack.
15. Maintain an implementation log in `docs/PHASE_REPORTS.md`. After each phase, record files implemented, tests run, test results, commit hash, and any limitations.
16. Never claim verification that was not actually executed.
17. Use a local single-user operating model for this MVP. Do not invent organization accounts, enterprise permissions, or authentication features outside the assignment.
18. No automated real-world outreach. The approval workflow must work, but approved messages remain drafts ready for later export. Real email sending is out of scope.

---

# Technology stack

**Frontend**
- React + TypeScript + Vite
- Tailwind CSS
- shadcn/ui
- React Router
- TanStack Query
- React Hook Form + Zod
- Recharts
- Lucide icons

**Backend**
- Python 3.11+ supported environment
- FastAPI
- Pydantic v2 and pydantic-settings
- SQLAlchemy 2.x
- Alembic
- psycopg 3
- httpx
- BeautifulSoup for permitted HTML parsing
- Google GenAI Python SDK
- LangChain for useful agent tooling/orchestration
- pytest

**Database**
- Neon PostgreSQL
- pgvector
- JSONB for validated structured research results
- PostgreSQL indexes, foreign keys, and constraints

**Development**
- Windows PowerShell
- npm
- Python virtual environment
- Local Git
- No Docker requirement
- No paid dependencies

Use supported, compatible library versions. Inspect installed versions and actual API availability rather than inventing SDK methods or model IDs.

---

# Environment configuration

The root `.env` already exists.

Expected configuration:

```dotenv
DATABASE_URL=
DIRECT_DATABASE_URL=
GEMINI_API_KEY=
GEMINI_MODEL=
EMBEDDING_MODEL=
EMBEDDING_DIMENSIONS=768
APP_ENV=development
DEMO_MODE=true
ENABLE_REAL_EMAIL_SENDING=false
```

Some values or variable names may already differ. Inspect and adapt rather than replacing the user's configuration.

- `DATABASE_URL`: Neon pooled connection, used for runtime queries.
- `DIRECT_DATABASE_URL`: Neon direct connection, used for Alembic migrations.
- `GEMINI_API_KEY`: Server-side Gemini credential.
- Embedding model: use an actually available Gemini embedding model supporting the configured dimensions.
- Model names and embedding dimensions must be validated against the available provider API.
- Do not force a paid API model.
- Do not expose credentials in frontend code or logs.
- `.env.example` must contain placeholders only.
- Prevent `.env`, virtual environments, logs with secrets, and generated artifacts from entering Git.

If required credentials are missing or unusable, report exactly which configuration is required.

---

# Git workflow — mandatory throughout all phases

Before making changes:

1. Inspect the current directory, Git status, and existing tracked files.
2. If no repository exists, initialize Git locally.
3. If a repository exists, preserve its history and branch.
4. Verify `.gitignore` excludes secrets and generated files before staging anything.
5. Do not discard or overwrite unrelated user work.
6. Use meaningful, phase-specific commits.
7. After each phase, run `git status` and verify the commit contents.
8. Do not push or contact any Git remote.
9. Preserve all commit history for later GitHub synchronization.

Required commit naming:

```text
phase-0: initialize local application foundation
phase-1: implement neon database and core backend
phase-2: implement prospect management and ingestion
phase-3: implement grounded ai research pipeline
phase-4: implement embeddings and semantic retrieval
phase-5: implement personalized outreach generation
phase-6: implement human approval workflow
phase-7: implement live analytics and red dashboard
phase-8: harden application and verify end-to-end tests
phase-9: finalize local release and documentation
```

Only create a commit after the phase is complete and its acceptance criteria pass.

If Git identity is missing, use the developer's existing Git configuration or request the minimum required identity information. Do not invent an identity.

---

# Dashboard visual specification

**The attached image is the primary visual reference.**

Replicate its composition, proportions, layout hierarchy, card structure, spacing, and clean SaaS aesthetic as closely as practical.

Adapt the content to our SDR application.

### Theme

Replace the reference's blues with a coherent red palette.

Suggested design tokens:

```text
Primary red:          #D92D20
Primary hover:        #B42318
Dark sidebar:         #241315
Light red surface:    #FEF3F2
Primary background:   #F8F9FB
Card background:      #FFFFFF
Main text:            #161B26
Secondary text:       #667085
Border:               #EAECF0
```

Use darker and lighter red shades for chart series, active navigation, selections, and accents.

Maintain accessible contrast.

### Exact layout direction

- Slim, dark vertical left sidebar with restrained white/red icons.
- White/light central dashboard canvas.
- Large prominent primary KPI card in the upper-left region, replacing the reference's blue card with red.
- Clean multi-series chart in the upper-right region.
- Smaller supporting statistic and trend cards.
- Wide analytical chart card in the bottom-left region.
- Supporting activity, approvals, and status cards on the right.
- Smooth rounded corners, consistent spacing, subtle borders, and polished typography.
- Desktop-first layout, with responsive tablet/mobile behavior.

Use the reference's visual geometry, **not its meaningless or illegible generated text**.

Do not copy its displayed money figures.

Our SDR project does not currently track deal revenue, so do not invent a revenue KPI simply because the reference has one.

Instead, the prominent KPI should show a meaningful computed metric, such as total prospects or qualified prospects.

### Every UI element must be functional

The frontend must not contain:

- Static dashboard numbers.
- Artificial chart data.
- Buttons without actions.
- Nonfunctional filters.
- Fake activity history.
- Fake growth percentages.
- Fabricated revenue.
- Lorem ipsum.
- Decorative sections with no product purpose.
- Unimplemented pages.
- Pretend research results.

Use actual API data. For zero records, display honest zero states and relevant actions.

---

# Phase 0 — Repository foundation and initial application

## Backend tasks

1. Inspect the root `.env` without printing its secret values.
2. Create the FastAPI project.
3. Configure Pydantic settings and root `.env` loading.
4. Configure secure environment validation.
5. Create a basic `/api/health` endpoint.
6. Add structured logging with secret redaction.
7. Configure development CORS for the local React application.
8. Add backend dependency management.
9. Establish project module architecture.
10. Add initial backend tests.

## Frontend tasks

1. Initialize React, Vite, and TypeScript.
2. Configure Tailwind and shadcn/ui.
3. Configure routing and TanStack Query.
4. Implement the main page shell and dark-red sidebar.
5. Establish the global typography, spacing, card, and color system.
6. Add shared loading, error, and empty-state components.
7. Implement a reusable typed API client.
8. Add basic routing for Dashboard, Prospects, Research, Outreach, Approvals, and Activity.
9. Ensure routing works without fake application data.

## Verification

- Backend starts locally.
- `/api/health` returns a real success response.
- Frontend starts locally.
- Basic navigation works.
- TypeScript compiles.
- No secrets are tracked.
- No fake metrics appear.

**Commit:** `phase-0: initialize local application foundation`

---

# Phase 1 — Database and backend foundation

## Backend tasks

Connect to the existing Neon PostgreSQL project.

Use SQLAlchemy and Alembic.

Create a robust database schema including:

### Companies
- UUID ID
- name
- normalized domain
- website URL
- industry when known
- created/updated timestamps

### Prospects
- UUID ID
- related company
- full name
- email if known
- job title
- location
- LinkedIn URL if supplied
- source and source URL
- notes
- status
- opt-out/do-not-contact flag
- created/updated timestamps

### Research records
- UUID ID
- company and prospect associations
- run status
- input snapshot
- structured findings
- errors
- timestamps

### Research sources and chunks
- source URL
- title
- fetched timestamp
- relevant evidence
- chunk text
- vector embedding
- source association

### Outreach drafts
- related prospect
- related research
- current approval status
- tone
- current version
- timestamps

### Draft versions
- draft association
- version number
- subject
- email body
- personalization
- CTA
- timestamps

### Approval events
- draft
- action
- associated version
- reviewer note
- timestamp

### Activity logs
- event type
- entity type/ID
- sanitized metadata
- timestamp

### Import jobs
- file identification
- total rows
- imported rows
- duplicates
- errors
- timestamp

Add foreign keys, unique constraints, sensible indexes, and pagination support.

Create an Alembic migration that ensures pgvector is available and creates the application schema.

Do not run destructive migrations against unrelated tables.

Use direct Neon connections for migrations.

## Frontend tasks

- Implement typed interfaces for the main database-backed entities.
- Connect frontend query hooks to the actual backend.
- Add database connectivity status where useful.
- Establish common API error presentation.

## Verification

- Alembic migration succeeds against Neon.
- Schema is visible in PostgreSQL.
- pgvector is available.
- Database create/read operations succeed.
- Foreign keys and constraints are verified.
- Existing Neon data outside the app is untouched.

**Commit:** `phase-1: implement neon database and core backend`

---

# Phase 2 — Prospect management and sourcing

## Backend tasks

Implement complete prospect CRUD:

- Create.
- Read.
- Update.
- Delete with explicit confirmation.
- Search.
- Filter.
- Sort.
- Paginate.
- Bulk operations.

Implement CSV import with:

- Header validation.
- Flexible column mapping.
- Preview before import.
- Clear row-level error reporting.
- Duplicate detection.
- Import status and summary.
- Transaction-safe persistence.
- File-size and row-count limits.

Support companies associated with multiple contacts.

Implement a practical **sourced discovery** feature:

- Accept user-supplied public company/directory URLs.
- Fetch permitted publicly accessible pages.
- Extract identifiable company information only when supported by source content.
- Preserve originating source URLs.
- Show extracted prospects/companies for confirmation before import.
- Never invent names, email addresses, titles, or businesses.
- Avoid scraping authenticated sites, bypassing access restrictions, or violating site policies.
- Do not attempt mass personal-contact harvesting.
- If broad public web discovery requires an unavailable search provider, clearly report that limitation rather than pretending it works.

Protect website fetching from SSRF, private-network access, unsafe redirects, oversized pages, and unreasonable request volumes.

## Frontend tasks

Create the complete Prospects workspace:

- Professional searchable data table.
- Pagination and sorting.
- Filters and status indicators.
- Add prospect dialog.
- Edit prospect dialog.
- Delete confirmation.
- Company detail view.
- CSV import workflow.
- Field mapping and import preview.
- Sourced discovery URL input and results preview.
- Empty states and error handling.
- Row actions to research or compose outreach.

## Verification

- New prospect persists after browser reload.
- Prospect edits and deletion work.
- Duplicate prevention works.
- CSV imports real rows correctly.
- Invalid files produce useful errors.
- Discovery results have verifiable source URLs.
- Frontend accurately reflects backend data.

**Commit:** `phase-2: implement prospect management and ingestion`

---

# Phase 3 — Real AI company research

## Backend tasks

Implement a grounded research pipeline using Gemini.

Workflow:

1. Receive prospect/company information.
2. Validate the website.
3. Retrieve permitted public website content.
4. Extract relevant content and metadata.
5. Collect source URLs and timestamps.
6. Pass structured evidence to Gemini.
7. Validate Gemini's structured output.
8. Persist the completed research result.
9. Update research status and activity logs.

The AI research response should include:

- Company overview.
- Verified industry, when available.
- Products/services found.
- Relevant potential business challenges.
- Qualification reasoning.
- Personalization opportunities.
- Suggested outreach angle.
- Supporting source references.
- Confidence and missing-information indicators.

**Crucial:** Separate source-supported facts from AI hypotheses.

Never present inferred pain points as verified company problems.

Implement:

- Research status lifecycle.
- In-progress progress reporting.
- Retry and timeout handling.
- Failed-fetch reporting.
- Validated structured AI responses.
- Research history.
- Re-run capability.
- Database persistence.
- Secure treatment of external webpage content as untrusted input.
- Durable job tracking so failed or interrupted research doesn't appear completed.

Use a simple local worker if needed. Do not require paid queues or Redis.

If a website is unavailable, support manual source notes that are explicitly labeled as user-provided.

Never fabricate successful research.

## Frontend tasks

Build the Research workspace:

- Prospect selection.
- Start research action.
- Real running status.
- Failed-research retry.
- Research detail page.
- Evidence/source panel.
- Source-supported facts.
- AI hypotheses clearly labeled.
- Research history.
- Qualification indicators.
- Actions to generate outreach from completed research.

Use clean, information-dense cards.

## Verification

- At least one accessible public test company website is processed successfully.
- Research contains actual source references.
- Generated research is stored in Neon.
- Refreshing the page preserves the results.
- Invalid and blocked URLs produce safe errors.
- Failed Gemini requests are reported accurately.
- AI-generated facts can be traced to stored evidence.

**Commit:** `phase-3: implement grounded ai research pipeline`

---

# Phase 4 — Embeddings, vector storage, and semantic retrieval

## Backend tasks

Implement the pgvector functionality completely.

- Integrate an available Google embedding model.
- Generate real embeddings from research chunks.
- Validate returned embedding dimensions.
- Store vectors in PostgreSQL using pgvector.
- Create appropriate indexing based on supported vector dimensions and actual dataset size.
- Implement cosine-similarity retrieval.
- Retrieve research chunks with their source URLs.
- Filter results by relevant company or prospect where appropriate.
- Prevent unrelated-company evidence from contaminating outreach.
- Handle embedding API failures gracefully.
- Preserve model information and embedding generation state.
- Re-embed when source research is regenerated, without leaving misleading stale vectors.

Use embeddings for genuine semantic retrieval, not merely storage as a checkbox feature.

The embedding integration must use the actual configured model and dimension supported by the API.

## Frontend tasks

Implement semantic research search:

- Search input.
- Returned matching research passages.
- Company/prospect context.
- Similarity score where meaningful.
- Source URLs.
- Helpful empty states.
- Research-to-outreach navigation.

## Verification

- Real research chunks produce real embedding vectors.
- Vector dimensions match the database schema.
- A semantic query returns meaningfully related research.
- Retrieval preserves source attribution.
- Missing embeddings are handled honestly.
- No fictional similarity results.

**Commit:** `phase-4: implement embeddings and semantic retrieval`

---

# Phase 5 — Personalized outreach AI agent

## Backend tasks

Implement an outreach drafting agent using Gemini and retrieved research context.

The agent must:

1. Receive a selected prospect.
2. Retrieve latest valid research.
3. Retrieve relevant evidence through semantic retrieval.
4. Generate personalized outreach grounded in actual information.
5. Produce structured output.
6. Save the generated draft.
7. Create an immutable version record.
8. Place the draft in the pending approval workflow.

Draft output:

- Subject line.
- Personalized opening.
- Main body.
- Value proposition.
- Call to action.
- Full composed email.
- Referenced research context.

Support tones:

- Professional.
- Concise.
- Friendly.

Support regeneration and draft-version history.

No fabricated achievements, fake mutual connections, invented prospect problems, unsupported offers, or invented company details.

Do not insert fabricated sender-company claims. Require a configurable sender identity/value proposition; if absent, use an honest generic draft structure or require the user to enter the missing information.

Do not send emails.

## Frontend tasks

Build the Outreach workspace:

- Prospect selector.
- Research preview.
- Tone selector.
- Sender/business context inputs.
- Generate button.
- Real loading state.
- Editable email subject and body.
- Draft preview.
- Saved draft list.
- Version history.
- Regenerate action.
- Pending approval status.
- Clear provenance of personalized claims.

The page must look like a professional outreach workspace rather than a chatbot.

## Verification

- Gemini creates genuinely different drafts based on different research.
- Draft content persists in Neon.
- Regeneration creates a new version.
- Editing does not destroy historical versions.
- A new draft is pending approval by default.
- No emails are transmitted.

**Commit:** `phase-5: implement personalized outreach generation`

---

# Phase 6 — Human approval queue and audit trail

## Backend tasks

Implement a robust approval state machine.

Statuses:

```text
pending
approved
rejected
archived
```

Allow:

- Review.
- Edit.
- Approve.
- Reject with optional note.
- Regenerate with previous history retained.
- Archive.
- Reopen rejected drafts through an explicit new review version.

Every transition must be validated and persisted.

Ensure:

- Invalid transitions are rejected.
- Review events are recorded.
- Approved versions are identifiable.
- Subsequent edits do not silently preserve approval of changed content.
- All actions produce activity records.
- The system never sends outbound messages automatically.

Approval is preparation for outreach, not evidence of actual delivery.

Support copying/exporting approved drafts without claiming they were sent.

## Frontend tasks

Build the complete approval interface:

- Pending queue.
- Draft review.
- Prospect/company research side panel.
- Email preview/editor.
- Approve button.
- Reject button.
- Regenerate button.
- Archive action.
- Approval history.
- Rejection notes.
- Search and filtering.
- Dynamic pending-count badge.
- Activity timeline.

Implement useful confirmation and error feedback.

## Verification

- Approval changes are saved.
- Rejection history is preserved.
- Editing approved content requires renewed approval.
- No invalid state transitions.
- Queue counts update immediately.
- Activity feed shows genuine persisted events.
- No sending occurs.

**Commit:** `phase-6: implement human approval workflow`

---

# Phase 7 — Fully dynamic red dashboard

This is the main visual development phase.

Use the attached design screenshot as the mandatory reference.

## Backend tasks

Implement genuine database-derived analytics:

- Total prospects.
- Researched prospects.
- Prospect qualification counts.
- Pending approvals.
- Approved drafts.
- Rejected drafts.
- Draft generation over time.
- Prospect creation trend.
- Research completion trend.
- Prospect status distribution.
- Company industry distribution.
- Recent activity.
- Approval turnaround where sufficient data exists.

Use SQL aggregations and appropriate API endpoints.

Growth rates must use real prior-period values with correct denominator handling.

Do not fabricate revenue, conversion rates, or outreach replies. Real sending and reply tracking are not in scope.

Never invent metrics to fill visual space.

## Frontend tasks

Rebuild the dashboard to closely match the attached visual reference.

Requirements:

- Red hero metric card.
- Compact dark sidebar.
- Large upper-right analytics chart.
- Lower-left wide pipeline/research chart.
- Supporting metric cards.
- Approval/status cards.
- Recent activity panel.
- Clean hover interactions.
- Consistent red chart palette.
- Professional typography.
- Responsive resizing.

Use Recharts for real interactive charts.

All charts load their data from real API endpoints.

Add:

- Working date-range filters.
- Meaningful tooltips.
- Responsive labels.
- Loading skeletons.
- Zero-data charts and cards.
- Empty-state navigation actions.
- Useful API error/retry states.

Do not retain the reference image's meaningless text or arbitrary figures.

## Verification

- Every displayed number maps to a real query.
- Every chart maps to live database aggregates.
- Adding a prospect changes relevant metrics.
- Completing research changes relevant metrics.
- Approving a draft changes queue and analytics counts.
- Refreshing the browser retains the correct values.
- Empty database shows zero/empty states.
- Visual style resembles the reference while using red.

**Commit:** `phase-7: implement live analytics and red dashboard`

---

# Phase 8 — Quality, reliability, and UI polish

## Backend tasks

- Improve input validation.
- Review SQL transaction handling.
- Verify migration reproducibility.
- Add API error consistency.
- Add pagination edge-case tests.
- Add rate limiting where appropriate.
- Add outbound HTTP fetch safeguards.
- Harden URL normalization and duplicate detection.
- Verify research source grounding.
- Verify embedding failures.
- Verify Gemini API error handling.
- Test interrupted/failed research jobs.
- Review logging for secrets and sensitive records.
- Add robust unit and integration tests.

Use mocks in unit tests, but perform separate real integration checks using the configured services.

Do not run destructive test cleanup on the application's ordinary data. Use isolated test data/schema or a dedicated test database where needed.

## Frontend tasks

- Remove broken interactions.
- Eliminate unnecessary animations.
- Fix layout overflow.
- Verify all table actions.
- Ensure modal forms work.
- Implement consistent success/error feedback.
- Verify keyboard navigation and contrast.
- Fix loading states.
- Fix mobile/tablet responsiveness.
- Ensure charts display correctly with zero data.
- Remove unused components.
- Remove filler content.
- Eliminate console errors.
- Add meaningful frontend tests.

Use Playwright for practical end-to-end browser verification if available.

Capture local screenshots for visual inspection when supported.

## Verification

Run:

- Backend tests.
- Frontend tests.
- TypeScript build.
- Production frontend build.
- Lint.
- Database integration checks.
- Core workflow end-to-end tests.

Fix failures.

**Commit:** `phase-8: harden application and verify end-to-end tests`

---

# Phase 9 — Complete local acceptance and final delivery

Perform a full end-to-end local run.

## Required real acceptance sequence

1. Start backend and frontend.
2. Connect to Neon.
3. Confirm database migrations are applied.
4. Create a company and prospect.
5. Refresh and confirm persistence.
6. Import a valid CSV file.
7. Confirm deduplication and import totals.
8. Research a legitimate publicly accessible website.
9. Inspect retrieved evidence.
10. Generate embeddings.
11. Execute a real semantic retrieval query.
12. Generate a Gemini outreach draft.
13. Verify personalization is grounded in research.
14. Edit and save the draft.
15. Regenerate a new version.
16. Submit or retain the draft for approval.
17. Approve one version.
18. Reject another.
19. Verify the audit trail.
20. Verify dashboard metrics and charts reflect the stored actions.
21. Reload the entire application.
22. Confirm all persisted records remain available.
23. Verify no email was sent.
24. Verify `.env` is not tracked by Git.
25. Run all final tests and builds.

Perform these actions against controlled test records. If any step cannot actually be executed, disclose it rather than reporting a false pass.

Do not manufacture successful test results.

## Documentation

Write a professional root `README.md` containing:

- Project overview.
- Features.
- Architecture.
- Technology stack.
- Directory structure.
- Neon and pgvector setup.
- Gemini configuration.
- Environment variables.
- Local installation.
- Backend commands.
- Frontend commands.
- Worker commands if applicable.
- Database migration commands.
- Testing commands.
- Troubleshooting.
- Limitations.
- Data provenance and research safeguards.
- Approval-only/no-auto-sending behavior.

Create `docs/LOCAL_ACCEPTANCE_REPORT.md`.

Create `docs/PHASE_REPORTS.md` with all phase records.

Create a `.env.example` with safe placeholders only.

Provide PowerShell-friendly commands or scripts, ideally:

```powershell
.\scripts\setup-local.ps1
.\scripts\start-local.ps1
.\scripts\test-local.ps1
```

These scripts must genuinely exist and work. If a single launcher cannot reliably manage all services, provide separately verified commands instead.

## Final acceptance requirements

The project is complete only if:

- Frontend runs locally.
- Backend runs locally.
- Neon persistence works.
- pgvector is genuinely used.
- Gemini is genuinely used.
- Prospect ingestion works.
- Research works against real permitted sources.
- Outreach generation works.
- Approval queue works.
- Activity records persist.
- Dashboard is dynamic.
- Red UI matches the reference's visual direction.
- No fake data is presented as real.
- Required tests pass.
- No secrets are committed.
- Local Git phase commits exist.
- No GitHub push/deployment has been attempted.

**Commit:** `phase-9: finalize local release and documentation`

---

# Required reporting format after each phase

At the completion of each phase, provide:

```text
PHASE:
STATUS: PASS / BLOCKED / FAIL
BACKEND COMPLETED:
FRONTEND COMPLETED:
DATABASE CHANGES:
TESTS EXECUTED:
TEST RESULTS:
LOCAL GIT COMMIT:
KNOWN ISSUES:
NEXT PHASE:
```

Reports must represent actual observed results.

Do not call an untested feature complete.

Do not commit a failing phase.

If a required external dependency is genuinely unavailable, document the exact blocker. Do not replace the real integration with a hidden mock or hardcoded success response.

---

# Final reporting requirements

When all phases are completed, provide:

1. Complete implemented feature summary.
2. Backend and frontend architecture.
3. Database schema summary.
4. Actual AI and vector functionality verified.
5. Exact local startup commands.
6. Final automated test results.
7. End-to-end acceptance results.
8. Actual Git commit history.
9. List of known limitations.
10. GitHub synchronization instructions for when repository access becomes available.

The application should be ready for a professional demonstration of the developer's capabilities, with real full-stack behavior and no misleading functionality.

**Start with Phase 0. Execute each phase sequentially, test it, commit it locally, report results, and continue through Phase 9 until the complete MVP is functional. Do not stop after scaffolding or generate an implementation plan without writing the code.**