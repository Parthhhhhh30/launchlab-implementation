# LaunchLab v2 visual experience — supplementary release audit

## Design diagnosis

The v1 standalone workspace opened with a generic six-tab side navigation and a list of unresolved checkboxes. Although operationally useful, a hiring manager scanning a link would have needed to learn the UI before discovering its point. This version adds an original, editorial, narrative landing page separate from — but connected to — the working studio. It avoids copying Metaview brand assets and deliberately separates user-facing narrative from proof of functional delivery.

## Execution claims / boundaries

- Live interactive actions from `/` call the **same** stateful FastAPI API as `/studio`, backed by PostgreSQL in production.
- Criterion revision invalidates fictional sign-off. Field mapping is a genuinely executed deterministic source transformation. Breaking it fails; repairing and rerunning passes.
- Engagement graphic and initial seven-gate/4-of-11 figures are a **synthetic kickoff baseline**, not live product telemetry. Live lab uses current saved workspace values and revision.
- The mini enablement exercise does **not** certify a real learner or affect implementation state; the full studio records explicitly simulated training checks.
- No real Metaview account, ATS integration, LLM, authenticated customer, production recruiting data, hiring decision or measured commercial result is claimed.

## v2 local verification

- 18 pytest checks including experience routes.
- Existing studio browser workflow across 16 meaningful operations still tested.
- New browser experience smoke checks API mutation, failed/repaired mapping, reload persistence, teaching explanation, and mobile 390px layout.
- Original desktop and mobile evidence screenshots preserved, new `experience-desktop.png` and `experience-mobile.png` generated.

## Release gates outstanding until performed

- Actual GitHub commit and Vercel READY status for this revision.
- Production `/`, `/studio`, `/api/health`, `/static/experience.js` response checks.
- Full live change -> reload persistence check and production UI review.
- Independent Claude/Codex execution not claimed. WCAG AA certification not claimed.

---

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
