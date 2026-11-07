# Release verification — LaunchLab
**Last reviewed:** 7 November 2026

## Scope

One public case-study site, one implementation studio and one AI-instruction evaluation clinic. The project uses fictional customer and applicant data. There is no real ATS integration or customer rollout.

## Verified behaviours

- The original local domain/API test suite passed during development; additional AI lab tests were run with explicitly mocked provider responses.
- A Chromium workflow exercised configuration edits, review, go-live gates, evidence checks, pilot launch, adoption interventions, handover, reload persistence and mobile layout.
- The public Vercel deployment reached READY, the homepage and clinic loaded, and Neon/PostgreSQL health was verified.
- Real model inference was verified after replacing the previously unavailable Gemini 2.5 Flash-Lite with Gemini 3.1 Flash-Lite and increasing the server-side timeout. The first successful baseline run returned six structured judgments, allowed citation IDs and a 6/6 reference agreement on *synthetic* cases.
- The project owner confirmed that the baseline/refined comparison works in their browser. That second run was not independently revalidated using the external browser-test service.

## Safeguards

- No public API key, no arbitrary candidate upload, no hiring decisions.
- Rule changes invalidate prior approvals. Mapping edits invalidate previous mapping validation.
- New intervention records do not change adoption figures by themselves.
- Input and structured-output validation, request quotas, source revisions, and JSON export.
- All test fixtures and expected labels are fictional.

## Limits

Not a third-party compliance audit, audited WCAG certification, fairness assessment or production-ready recruiting platform. No actual authenticated customer approvals, Metaview account, Greenhouse connection, commercial ROI or real-world user-adoption measurements.

These statements are scoped to the checks performed. Product quality and model outputs must continue to be evaluated separately from deployment success.
