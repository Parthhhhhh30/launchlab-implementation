# LAUNCHLAB — AI Recruiting Implementation & Adoption Studio

**Independent functional portfolio exercise. Not affiliated with Metaview or Greenhouse.** All customer, team, applicant, usage and training data are fictional; none of the simulated activities are verified commercial results.

> **Recruiter walkthrough (90 seconds):** [Demo guide](docs/DEMO_GUIDE.md) · [Release audit](docs/RELEASE_AUDIT.md)

## What this actually does

LaunchLab models a single fictional customer, Northstar Labs, from unapproved recruiting requirements through an implementation readiness check, enablement, staged pilot, adoption-recovery decisions and synthetic handover.

The **working state machine** protects consequential transitions:

- A vaguely worded hiring requirement cannot be marked reviewed. Editing any requirement invalidates customer sign-off.
- A synthetic ATS field-map is **actually transformed and validated** against fictional input data. Change `job.id` to `job.invalid`, rerun, and the check fails; repair it and rerun to pass. A user cannot manually override the mapping test.
- The pilot cannot launch until hiring criteria are reviewed, the fictional owner signs off, all simulated checks have evidence, training exercises are completed and at least six of eleven fictional users are trained.
- The adoption area distinguishes weekly active usage from onboarding attendance; a planned intervention **never** increases usage without a separate observation.
- Handover is blocked until there is a complete simulated week-two observation and at least eight active users.
- Every accepted action increments a server-side revision and is recorded. Concurrent stale edits return HTTP 409 instead of silently replacing another tab's changes. Reloading retains the data.
- The export includes the complete synthetic state, evidence and derived readiness/adoption metrics.

No external recruiting platform is connected and no applicants are evaluated, ranked or rejected. The integration checks other than the schema-mapping test are human-entered fictional dry-run records.

**Public research references:**
- Metaview Implementation Specialist: https://jobs.ashbyhq.com/metaview/846deb54-759a-4486-9e31-f4cde42dce91
- Metaview 30-question AI screening evaluation: https://www.metaview.ai/resources/blog/ai-screening-tool-evaluation-rubric
- Metaview customer cases: https://www.metaview.ai/resources/case-study/deel-hiring-metaview-reports ; https://www.metaview.ai/resources/case-study/lightspeed-boosts-recruiter-productivity ; https://www.metaview.ai/resources/case-study/elara-caring-saved-recruiter-time-screening

## Architecture

- **Frontend:** bespoke responsive HTML / CSS / vanilla JavaScript; no template starter, UI kit or remote JS CDN. Public Google Fonts are optional and the fallback remains usable offline.
- **Server:** FastAPI with schema-checked action allowlist and deterministic rules in `domain.py`.
- **Persistent state:** a real SQLite database for local use, or a PostgreSQL database supplied via `DATABASE_URL`/`POSTGRES_URL` for serverless hosting. Workspaces are isolated by a cryptographically random cookie and use serialized, transactional revision checks. Separate namespaces avoid touching unrelated tables in an existing database.
- **Case model:** versioned JSON document per anonymous demo workspace. This is appropriate for an isolated demonstration, not a production multi-tenant SaaS database.
- **Safety:** only synthetic records; no sending emails, uploading CVs, accessing real ATS accounts, authenticating fictional approvers, or making hiring decisions. On the hosted version, **the app fails closed without PostgreSQL** rather than claim persistent saving on an ephemeral serverless disk.

## Local development (no paid service or API key needed)

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
python -m uvicorn server:app --reload
```

Open `http://127.0.0.1:8000`. SQLite is created in `data/launchlab.sqlite3`. Data is persistent until that file is deleted; reset creates a new isolated workspace, retaining the old database record.

## Checks

```sh
python -m pytest -q
python tests/browser_smoke.py
```

Browser smoke testing uses actual Chromium and the real FastAPI + SQLite backend, with request bridging because the execution sandbox forbids browser navigation to localhost. It changes sixteen meaningful states, checks persistence and takes desktop/mobile screenshots. See `docs/RELEASE_AUDIT.md`.

## Deployment

Vercel Python/FastAPI runtime, `vercel.json`, and requirements are provided. A **private `DATABASE_URL`** (a PostgreSQL connection string for a dedicated launchlab database or isolated prefix) is required for durable hosted writes. Never expose or commit the connection string. The official Vercel-Neon Marketplace has a free tier, but provisioning/connection must be verified separately; no paid plan is assumed. Run tests before promoting the deployment.

Hosted app should be tested by making a change, reloading, opening a second tab to test revision conflict, exporting the evidence and completing the full pilot/adoption scenario. The `/api/health` endpoint reports whether PostgreSQL is active.

### Hosting limitations and threat model

This is a **public, untrusted portfolio demo** and is not an enterprise application. The demo cookie is an unguessable bearer session, not a logged-in identity; the audit records typed actions without real approver authentication. No personal identifiable applicant information should be entered. A visitor can write synthetic data into their isolated workspace but should not be given permission to view any other workspace. There is an action cap, input bounds and same-origin JSON enforcement, but no platform-wide abuse quota, CAPTCHA, full rate-limiter, retention-cleanup job or authenticated sharing. The implementation must not be connected to production customer databases or used as a compliance control without substantial hardening.
