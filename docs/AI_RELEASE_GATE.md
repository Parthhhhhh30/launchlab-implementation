# AI model operations and verification

## Live model

The server currently requests `gemini-3.1-flash-lite` through Google's `generateContent` API using `GEMINI_API_KEY`. Keys are read only in the server runtime; no API key is embedded in the browser or repository.

The application accepts two editable instruction versions, fixed synthetic fixtures, and structured JSON output. Each result is validated for allowed case IDs, allowed labels, evidence IDs and response sizes. Citation validity does not establish semantic correctness.

Six reference judgments were authored for this fictional exercise. Their agreement rate is an **illustrative regression check**, not a general accuracy or fairness metric.

## Usage limits

Server-side transaction controls reserve at most three calls per anonymous workspace and twelve globally per UTC day, including failed provider calls. Google additionally enforces its own project-level quotas. There is no paid-provider fallback. To avoid billing, the operator must ensure the Google project itself remains on the Free tier without active billing. Costs cannot be controlled by an application flag alone.

## Reproducible check

1. Confirm `/api/health` reports a functioning database.
2. Open `/agent-lab`; the page must report the configured model without exposing a key.
3. Run Version A against six fictional cases; review citations, labels, follow-up questions, model ID and token usage.
4. Run Version B on the same cases. Inspect differences; do not assume either instruction version necessarily wins.
5. Refresh and confirm the saved runs remain visible.
6. Try invalid citations, missing evidence and stale revisions in local tests.

## Tested and not tested

A real baseline inference with Gemini 3.1 Flash-Lite succeeded in production on 7 November 2026: six outputs, six allowed evidence references and six matches to the synthetic labels were displayed. The user has also confirmed seeing the two-version comparison. The model may behave differently on subsequent runs.

The deterministic map validator does not connect to Greenhouse. This project has no real users, authenticated approvals, real recruiting datasets, or autonomous hiring actions.

## Security boundary

Workspaces use random cookies rather than account authentication. Public users should enter only fictional content. A production system handling real applicants would require data protection controls, permissions, audit authentication, abuse monitoring, consent and retention policies beyond this demonstration.
