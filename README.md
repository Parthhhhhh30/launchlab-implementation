# LaunchLab

A customer-implementation workbench for the gap between signing a contract and seeing consistent adoption.

[Live application](https://launchlab-implementation.vercel.app/) · [Implementation studio](https://launchlab-implementation.vercel.app/studio) · [Agent configuration lab](https://launchlab-implementation.vercel.app/agent-lab)

A fictional customer rollout connects requirements, integration checks, go-live conditions, training, adoption observations and handover. A separate AI lab compares instruction versions against six fixed fictional evidence cases.

## Try the workflow

1. Clarify an ambiguous brief. Editing it invalidates earlier approval until it is reviewed again.
2. Change the synthetic ATS mapping from `job.id` to `job.invalid`, inspect the validation error, repair it and retest.
3. Investigate a pilot with four of eleven weekly-active users. Recording an intervention does not change adoption; an explicit new usage observation is required.
4. In the configuration lab, edit two instruction versions, request live model evaluations and compare their evidence IDs, follow-up questions and agreement with human-authored reference labels.

The studio also tracks learning checks, approval invalidation, revision conflicts, handover readiness and JSON evidence exports.

## How it works

FastAPI owns rule-based transitions, validation and versioned workspace records. The hosted app uses Neon PostgreSQL; local development uses SQLite. Transactions and revision checks prevent stale updates from silently replacing newer work. The interface uses HTML, CSS and JavaScript.

The optional Gemini integration is configured for `gemini-3.1-flash-lite`. Its key stays server-side. Evaluation records retain instructions, model, version, timestamp, token usage and output. Returned evidence IDs are checked against the fixtures.

Public inference is limited to three calls per anonymous workspace and twelve globally per UTC day; failed calls count. There is no automatic paid-provider fallback. Actual availability and cost depend on the provider account's billing settings.

## Run locally

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
python -m uvicorn server:app --reload
```

Open `http://127.0.0.1:8000`. SQLite works without a cloud account. Live inference requires a privately configured server-side `GEMINI_API_KEY`. Hosted persistence requires a separate PostgreSQL database through `DATABASE_URL`.

```sh
python -m pytest -q
```

The [quality workflow](.github/workflows/quality.yml) tests persistence, approval invalidation, mapping recovery, adoption rules, isolation, revision conflicts and malformed model outputs, then compiles the Python source. Mocked-provider tests do not establish live Gemini access. Additional browser checks and historical release evidence are in the [walkthrough](docs/DEMO_GUIDE.md), [model operations](docs/AI_RELEASE_GATE.md) and [release audit](docs/RELEASE_AUDIT.md).

## Boundaries

Northstar Labs, applicant examples, usage figures, training records and integration fixtures are synthetic. The app makes no employment decisions and connects to neither Metaview nor Greenhouse. It is independent and unaffiliated with either company.

Six cases do not establish model accuracy, fairness or commercial return. A valid evidence ID does not prove correct interpretation. Training and approval entries are self-recorded, not authenticated customer actions. Anonymous workspace cookies provide isolation, not user identity. Do not enter real personal or applicant information.

Built with AI-assisted coding and functional testing. This is a portfolio prototype, not a production recruitment system or evidence of unaided programming or client implementation.

Scenario context came from public [Metaview implementation-role information](https://jobs.ashbyhq.com/metaview/846deb54-759a-4486-9e31-f4cde42dce91) and [case studies](https://www.metaview.ai/resources/case-study); neither is an endorsement.
