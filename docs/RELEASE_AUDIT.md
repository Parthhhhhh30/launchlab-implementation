# LaunchLab release audit — 7 November 2026

## Release standard

The application must demonstrate end-to-end functional behaviour with meaningful state transitions, persistent storage, accurate records, readable UI, no hard-coded business success and clearly labelled synthetic data. Do not mark deployed or production-ready until the hosted persistent database and complete browser tests have been independently verified.

## Executed checks

- **Domain + API regression:** `python -m pytest -q` — 17 passed (as of initial completion).
- **Real Chromium UI test:** `python tests/browser_smoke.py` — passed, completing 16 recorded operations including criteria edit/review, approval, validated synthetic ATS map, evidence checks, training, pilot launch, adoption intervention, usage recording and handover.
- **Persistence:** browser-backed SQLite state reload check passed; test database is separate from the normal development database.
- **Responsive:** Chromium mobile viewport 390 × 844; no horizontal overflow in the tested command-room view.
- **Safety:** tests cover origin enforcement, content-type restrictions, per-visitor session isolation, optimistic revision conflicts, hold on incomplete evidence, audit events, misuse of numeric counters and invalid mapping paths.
- **Source-code review:** no live candidate PII or ATS credentials in repo; no automated hiring decisions.

## Adversarial findings fixed during development

1. **UI review dead-end:** originally hid the review action by including the `reviewed=false` flag in the test for whether the action should be shown. Fixed and re-exercised.
2. **Form navigation bug:** an input named `id` masked a form's `id` DOM property, bypassing submit interception and navigating to a query string. Fixed by reading `getAttribute('id')`. Re-exercised the complete workflow.
3. **Insufficient technical evidence:** manual checkbox-style ATS mapping verification could be marked passed without any real validation. Replaced with deterministic synthetic transformation, separate map editing, automatic pass/fail and invalidation.

## Unverified / not claimed

- Live Neon PostgreSQL persistence until deployment, endpoint configuration and reload checks are actually performed.
- Any actual Metaview feature access, Metaview customer training, Greenhouse integration or external collaboration.
- Real customer outcomes, hiring scores, benchmark reliability, or independently measured ROI.
- Accessibility WCAG AA audit using a specialist tool, although keyboard focus, semantic controls, responsive layouts and status announcements are included.
- Use of an external Codex or Claude Code runtime. Those CLI tools were not accessible in the local build environment; development and QA were performed here and can be independently reviewed in either app later.

## Release decision

**Local working build: VALIDATED.** Hosted public release remains contingent on a real persistent database, deployment and live functional verification. This prevents confusing a working local build with a complete hosted release.
