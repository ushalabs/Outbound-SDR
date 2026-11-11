# Final live UI test results

11 November 2026 · Chrome → normal application → normal persistent database

**Four complete workflows passed. One was blocked by real Gemini HTTP 503 high demand after retries.** No successful analysis or draft is claimed for the blocked case.

| Case | Small business | Result | Saved review state | Research evidence |
| --- | --- | --- | --- | --- |
| SMB01 | Carla Seed Accountancy | PASS | approve | public website |
| SMB02 | Summed Up Accountancy | PASS | pending | public website |
| SMB03 | Morris Accountancy Services | PASS | reject | public website |
| SMB04 | Adena Accountancy | PASS | archive | User-provided notes summarized from the verified official contact page |
| SMB05 | Go Figure Financial | BLOCKED | No draft created | Research attempted; Gemini 503 prevented completion |

## What was tested

Each completed workflow used a real practice and its published contact details: CSV import, reload persistence, source-backed Gemini research, evidence inspection, actual embedding generation, semantic retrieval, tailored outreach, human editing into v2, historical-v1 comparison, the stated review action, a browser reload, and a final test ledger saved into the prospect notes. Carla Seed also exercised exact-version approval and JSON export, with `delivery_status: not_sent` verified.

The five-row CSV imported successfully into the real database. Re-importing it showed five duplicates. The contact values and final test ledgers for all five practices were read back through the UI after reloading.

## Open the actual saved records

### SMB01 — Carla Seed Accountancy

- Official source: [https://www.carlaseed.co.uk/](https://www.carlaseed.co.uk/)
- Published business email: info@carlaseed.co.uk
- Published business phone: 07730 31 41 51
- [Saved research/history](http://127.0.0.1:5173/research?prospect=75a12d3a-c4a6-48a2-a746-3019609049b0)
- [Saved draft/version/review](http://127.0.0.1:5173/approvals?draft=39fd9749-a0e9-4ca2-ab63-b89390a49e87)
- Final outcome: **PASS** — approve
- [Database note read-back screenshot](../../artifacts/manual-live/SMB01-persisted-ledger.png)

### SMB02 — Summed Up Accountancy

- Official source: [https://summed-up.co.uk/contact/](https://summed-up.co.uk/contact/)
- Published business email: enquiries@summed-up.co.uk
- Published business phone: 0161 505 1978
- [Saved research/history](http://127.0.0.1:5173/research?prospect=ff627263-f7c5-4242-8c28-be24d0b644da)
- [Saved draft/version/review](http://127.0.0.1:5173/approvals?draft=2f714b62-bf79-4ecd-930f-a2cbdb0bc9c0)
- Final outcome: **PASS** — pending
- [Database note read-back screenshot](../../artifacts/manual-live/SMB02-persisted-ledger.png)

### SMB03 — Morris Accountancy Services

- Official source: [https://morrisaccountancyservices.co.uk/contact/](https://morrisaccountancyservices.co.uk/contact/)
- Published business email: info@morrisaccountancyservices.co.uk
- Published business phone: 07967 253672
- [Saved research/history](http://127.0.0.1:5173/research?prospect=5060665e-9041-4866-be9e-599723ca565f)
- [Saved draft/version/review](http://127.0.0.1:5173/approvals?draft=ac1723a7-a51b-4e19-bbe6-472de0c48837)
- Final outcome: **PASS** — reject
- [Database note read-back screenshot](../../artifacts/manual-live/SMB03-persisted-ledger.png)

### SMB04 — Adena Accountancy

- Official source: [https://adenaaccountancy.co.uk/contact-us/](https://adenaaccountancy.co.uk/contact-us/)
- Published business email: info@adenaaccountancy.co.uk
- Published business phone: 0161 706 1847
- [Saved research/history](http://127.0.0.1:5173/research?prospect=aa92830a-c0cf-4d73-919f-dd7fb0804c44)
- [Saved draft/version/review](http://127.0.0.1:5173/approvals?draft=6ecc0fb5-e26c-4f61-8357-9da105173de2)
- Final outcome: **PASS** — archive
- [Database note read-back screenshot](../../artifacts/manual-live/SMB04-persisted-ledger.png)

### SMB05 — Go Figure Financial

- Official source: [https://www.gofigurefinancial.com/](https://www.gofigurefinancial.com/)
- Published business email: karen@gofigurefinancial.com
- Published business phone: 020 3700 8178
- [Saved research/history](http://127.0.0.1:5173/research?prospect=42edf529-d8f0-4569-badb-d53a73724a3f)
- Final outcome: **BLOCKED** — No draft created
- [Database note read-back screenshot](../../artifacts/manual-live/SMB05-persisted-ledger.png)

Go Figure has three failed research runs retained in the application, with genuine Gemini 503 errors. Its published business contact and prospect notes remain saved. There is no successful research, embedding set, or draft for this practice yet. When the provider is available, open the failed run and use **Re-run**; this is the intended next self-test.

## Retries and limits

Gemini was intermittently unavailable. Summed Up and Adena recovered on retry; Go Figure remained blocked. Adena’s completed run used labeled user-provided notes summarizing its verified official contact page. It is not presented as an automatically fetched successful website analysis. The source label was inspected in the actual Research screen.

The raw attempt log remains in `live-results.json`. Initial browser-control lookups for a prefilled textarea were corrected and retried; final outcomes above are the verified current states. Older failed/provider-error runs remain visible in the database.

No mocks, direct API writes, SQL fixtures or disposable database schemas were used for these five cases. No messages were sent. Review outcomes are testing states and do not establish buying intent. Website availability and published contact details were checked; mailbox deliverability and operational staffing sizes were not verified.

The dashboard currently includes **27 total prospects**, because earlier broad-company trial records remain in the same workspace. Only the five practices above belong to this small-business test pack. Search the company names to locate them; their Notes start with `SMB REAL BUSINESS TEST SMB0x`.

## Try it yourself

Use [MANUAL-TESTING.md](MANUAL-TESTING.md) for repeatable UI steps. Import [the five-business CSV](real-small-business-prospects.csv) to test duplicate detection, or [the fresh two-practice CSV](fresh-small-businesses-for-your-test.csv) to add NMR Accountants and AAC Consultancy yourself. Those two have not been imported by the tester.
