# LaunchLab real-model release gate — 7 November 2026

## Research-based free-tier provider

Google Gemini Developer API (Google AI Studio), stable `gemini-2.5-flash-lite` model. Google's published free tier includes zero-cost input/output tokens **subject to current quotas and Google account terms**. Requires the owner to create an API key for a project explicitly marked *Free* without activating billing. ChatGPT Plus, Claude Pro and Cursor Free do not provide this API key or guarantee production API inference usage.

Primary documentation: https://ai.google.dev/gemini-api/docs/pricing and https://ai.google.dev/gemini-api/docs/billing

## What was built

- Standalone accessible `/agent-lab` configuration clinic linked from the existing homepage, preserving the original studio.
- Two customer instruction versions, editable and versioned in each isolated PostgreSQL workspace.
- Exactly six synthetic evidence cases with fixed human reference labels (including ambiguous claims and an injection attempt).
- Real server-side inference with Gemini `generateContent`, structured JSON and hard-validated evidence IDs, labels and response lengths.
- Per-workspace (3) and global (12) persistent daily request quotas, checked atomically before provider calls, errors included; no paid fallback.
- Per-run provenance (model ID, instruction text/version, server timestamp, output, citation checks and reference agreement); no autonomous hiring recommendations.

## What must not be claimed

- A live model invocation has occurred until a **free-tier** `GEMINI_API_KEY` is configured and a provider request has actually returned a structured validated response.
- Six synthetic reference labels are not evidence of real-world accuracy or fairness, and prompt differences are only measured where both versions were actually run.
- No real recruiting data, Metaview product access, live Greenhouse connection or external client training was involved.
- No fully guaranteed $0 usage if the operator links a billed API project; use a genuinely Free project with no billing enabled and monitor API usage.

## Manual account step (only when activating real AI)

1. Visit https://aistudio.google.com/apikey; create or select an API project marked Free (no billing), generate a key. Never put the key into GitHub, a chat message, browser JS, or public screenshots.
2. In Vercel project `launchlab-implementation`, Settings → Environment Variables, add `GEMINI_API_KEY` as a **Sensitive** environment variable for Production. Do not enable paid billing. The owner must perform this action; ChatGPT does not request the value.
3. Redeploy the existing production project. Check `/api/ai/status` from the same browser session reports `available:true`; run baseline and refined prompts, confirm actual outputs, citations and preserved revision/run records.
4. Confirm 429 handling, second-visitor isolation, daily limits and that changing instructions preserves earlier run provenance. Only then call the real-model release COMPLETE.

## Security scope

The endpoint accepts only the fixed synthetic fixtures, never arbitrary uploaded CVs. Anonymous visitors may edit their own instructions with a strict character cap. A cryptographically random session cookie partitions workspaces but is not a login system. This is a low-volume public portfolio exercise, not production hiring software or compliance-certified recruitment tech.
