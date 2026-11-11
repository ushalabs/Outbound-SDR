# Reference-led frontend redesign — 2 November 2026

The user supplied a new visual reference and requested its color scheme and
structure for Outbound SDR Agent. This replaces the earlier light/red direction.
All application changes are confined to the frontend.

## Direction

- Product: research prospects, write grounded outreach, and review draft versions
- Character: focused, expressive, precise
- World: an outbound operations workspace in near-black and charcoal
- Moments: violet daily activity, lime pipeline trends, and large real metrics
- Signature: a pill-based header and the evidence → draft → review workflow

The reference provides the black frame, charcoal panels, violet/lime palette,
light active navigation, white actions, large summary row, and three-panel rhythm.
Its finance data, personal identity, branding, and image assets were not copied.
The screenshot's colored backdrop is recreated in CSS because the user explicitly
requested the same color scheme and structure.

## Nine passes

1. **Spacing:** a compact summary row, consistent panel padding, and smaller gaps
   replace the former oversized card arrangement.
2. **Color:** near-black shell, charcoal working surfaces, violet activity marks,
   lime prospect trend, white primary controls, and semantic warning/error states.
3. **Icons:** the existing Lucide set is retained, including functional links to
   prospect search, research, outreach, activity, and the approval queue.
4. **Copy:** interface text remains specific to the actual SDR workflow. No fake
   revenue, contacts, performance claims, messages, or account identities were added.
5. **Type:** a system sans interface, lighter headings, larger primary metrics,
   and tabular figures follow the reference's hierarchy.
6. **Layout:** horizontal pill navigation replaces the sidebar. The dashboard
   presents a summary strip followed by pipeline, outreach, and recent-work panels.
   Prospect breakdown and review metrics remain available below. Header tabs scroll
   horizontally on phones, while working panels stack at smaller widths.
7. **Details:** input, table, badge, citation, dialog, editor, selection, and focus
   treatments now share the dark palette. The icon and browser theme match it too.
8. **Visuals:** charts and calendar cells use persisted analytics only. Zero-count
   days remain zero. The calendar shows generated drafts per day, with exact dates
   and review decision counts in its tooltips; it does not imply hourly data.
   No bitmap generation was required.
9. **Motion:** brief color/surface transitions and existing loading behavior only;
   the header remains available while scrolling, and reduced motion is respected.

## Functional scope

The analytics API, all six routes, prospect CRUD, CSV mapping/import, discovery,
research and source inspection, embedding/search controls, draft editing/version
history, approvals/rejections/reopening, reviewer notes, and approved-only export
are retained. The week/month/quarter controls select the existing 7/30/90-day
ranges. Custom dates remain available through the calendar control.

No backend, migration, credentials, model selection, or sending behavior was
changed. Real empty workspace states remain visible. Test records are created
only by the existing isolated acceptance harness and cleaned afterward.

## Verification

- TypeScript and production build: passed
- ESLint and 5 frontend unit tests: passed
- Normal browser suite: 3 passed, with isolated-only cases skipped in that run
- Isolated populated dashboard: passed, including reload and date filters
- Isolated prospect create/reload/edit/detail/delete workflow: passed
- Full live workflow: passed with real Gemini research, embeddings, retrieval,
  generation, version edits/regeneration, approval/rejection/reopening, audit,
  JSON download, and persisted dashboard counts; zero console/resource errors
- All six pages at desktop and phone widths: no horizontal overflow or page errors
- All six mobile navigation actions and the mobile prospect dialog: passed
- Changed-file formatting and Git whitespace checks: passed

The numeric metric assertion initially included the new adjacent caption; the
numeric value now has its own element. An initial live run was interrupted by a
Vite reload while the browser theme was being edited. The complete rerun against
finished assets passed. All isolated schemas were cleaned by the existing harness.

Screenshots are stored in `artifacts/reference-redesign/` in the project root
(ignored local artifacts). The `*-live-workflow.png` previews show isolated test
records and are distinct from the ordinary empty workspace.

## Credits

Visual direction: the user-provided dashboard reference, bearing
@heyradiant.studio. Implementation retains Outbound SDR Agent's own branding.
Workflow informed by [Unslop](https://github.com/heydamir/unslop), created by
Damir Sokolovsky ([@heydamir](https://x.com/heydamir)), CC BY 4.0. The user's explicit
reference and structure instructions take precedence over its default preference
for neutral backgrounds and retaining an existing sidebar.

## Follow-up cleanup — 11 November 2026

Removed the colored outer backdrop and frame. Removed redundant captions and page introductions across all six pages. Restored the application logo and browser favicon to red, with a versioned favicon URL. The chart accents remain. All six routes passed desktop and phone viewport checks without overflow or page errors after the cleanup.

CSV import now separates the original file header from the field it saves into, using readable destination names. Completed imports show a compact result and Done action. Contacts without a supplied personal name display their existing business email or company name. Outreach uses direct email-writing labels and retains evidence references under Sources used. Future email generation is instructed to use plain business language while preserving evidence and uncertainty rules; existing saved drafts are unchanged.

Validation: 22 backend unit tests and 5 frontend tests passed, along with backend lint, frontend lint and production build. Chrome checks against the normal database covered existing contact display, CSV mapping edits and preview, mobile mapping layout, and an existing saved email. These follow-up checks made no database writes or Gemini requests.
