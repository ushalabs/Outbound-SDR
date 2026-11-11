# Live manual testing — small accountancy practices

Date: 11 November 2026 · normal app at http://127.0.0.1:5173

## Scope

Five specific local accountancy/bookkeeping practices were selected from their own
public websites. The test uses the normal UI and the normal connected database.
It does not use temporary schemas, mocked providers, direct API writes, or backend
unit-test fixtures. All imported records, research runs, evidence, vectors, drafts,
versions, review notes and activity remain saved for inspection.

The initial broad-company trial was superseded by the user's clarification and
is not counted in this report. Its earlier records remain in the workspace; this
report covers only the five practices in `PROSPECTS.md`.

## The five business cases

1. **Carla Seed Accountancy:** published contact Carla Seed, company email and
   Stockport service area. Research the real site, retrieve evidence, draft a
   consultation recap offer, edit to v2, approve exact v2, and download JSON.
2. **Summed Up Accountancy:** published business mailbox and discovery-call
   offering. Research the real site, retrieve evidence, draft a specific offer,
   edit with history preserved, and leave the draft pending for the user.
3. **Morris Accountancy Services:** published contact Vanessa Morris and general
   company mailbox. Research the real site and meeting availability, draft an
   offer, edit to v2, reject with an explanatory test note, and verify persistence.
4. **Adena Accountancy:** published Oldham practice and business mailbox. Research
   its actual services, retrieve evidence, draft and edit outreach, then archive
   with a test reviewer note while retaining the record.
5. **Go Figure Financial:** published bookkeeping services and business mailbox.
   Research and retrieve the available evidence, draft a relevant offer, edit
   with history preserved, and leave pending for user review. Any website-fetch
   limitation and manual-source fallback is explicitly identified in results.

No actual customer pain, purchasing intent, employee count, or existing commercial
relationship is assumed. Contact details are published business details, not
guessed email patterns. The offer uses UshaLabs' existing MeetingMinutes AI
capabilities: recordings/transcripts to reviewed minutes and action items.
Approval here is a manual test state. No email has been sent.

## Repeat the workflow yourself

1. Open **Prospects → Import CSV** and choose `real-small-business-prospects.csv`.
   Review column mappings and preview. Since these five records were already
   imported during the live run, expect duplicates; do not change contact names
   or addresses to bypass deduplication.
2. For a new import, use `fresh-small-businesses-for-your-test.csv`. NMR Accountants
   and AAC Consultancy are reserved for you and have not been imported by the tester.
   AAC's email is blank because the source reader masked it; its public contact
   page and business phone are provided instead.
3. Search a practice by its exact company name. Open its company details and
   inspect the published contact/source URL. Edit the prospect to read the saved
   **SMB live UI test** notes and the link to its draft.
4. Open **Research** from the prospect row. Select a completed run, expand
   **Inspect stored evidence**, and compare the facts with the linked official
   site. Potential challenges are hypotheses, not verified business problems.
5. Generate or refresh embeddings, then search `accountancy bookkeeping client
   consultations and meetings`. Inspect returned passages and similarity values.
6. Open **Compose from research**. Enter your real sender details and offer;
   generate a draft, compare its personalization to the actual company evidence,
   and edit it. Save and compare the original/current versions.
7. Open **Approvals**. Inspect reviewer notes and version history. Review one of
   the pending drafts, reject/reopen a rejected draft, or generate a new draft
   for an archived example. Only approve wording you have reviewed yourself.
8. For an approved version, use **Export draft**. Inspect `version` and
   `delivery_status` in the downloaded JSON. Exporting does not send the email.
9. Reload the page and inspect **Activity**. Imports, research, edits and review
   actions should remain visible. The dashboard includes all normal workspace
   records, including the earlier trial data, so its totals exceed five.

## Evidence and results

`live-results.json` records actual case outcomes, timestamps, checkpoints, source
URLs and direct local record links. Screenshots are in the project directory
`artifacts/manual-live/SMB01-*` through `SMB05-*`. The final results table and record links are in [RESULTS.md](RESULTS.md).

The raw attempt log is retained. A first attempt needed a corrected selector for
a prefilled offer textarea; that is a test-control retry, not a claimed provider
failure. Final outcomes reflect the completed rerun, and actual website errors
are reported separately if encountered.

## Verified final outcome

Four workflows passed; Go Figure Financial remains blocked by Gemini HTTP 503. It has no completed research, embeddings or draft. Adena’s completed research uses labeled user-provided notes from its verified source. See [the final report](RESULTS.md) for exact saved states and retry details.
