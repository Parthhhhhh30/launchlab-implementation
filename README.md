# LaunchLab
**From contract to adoption — an interactive AI implementation case.**

LaunchLab explores a question faced by teams adopting AI tools: what happens after the contract is signed but before users consistently see value? It combines a fictional customer rollout, a working implementation control system, and a real AI-instruction evaluation lab.

**Live:** https://launchlab-implementation.vercel.app/  
**Agent configuration lab:** https://launchlab-implementation.vercel.app/agent-lab  
**Implementation studio:** https://launchlab-implementation.vercel.app/studio

The fictional customer is Northstar Labs. All applicant examples, usage figures, training records and integration fixtures are synthetic. LaunchLab is independent; it is **not affiliated with Metaview or Greenhouse**, does not connect to their platforms, and makes no employment decisions.

## Try it

1. **Clarify a brief:** Turn an ambiguous requirement into an observable one. Changes invalidate earlier approval until reviewed again.
2. **Break an integration:** Change the synthetic ATS mapping `job.id` to `job.invalid`, run the validator and inspect the error. Repair the mapping and retest.
3. **Investigate adoption:** The fictional pilot begins with four of eleven weekly-active users. Record an intervention; usage does not change until an explicit new observation is entered.
4. **Run the agent configuration clinic:** Edit two instruction versions, evaluate six fixed fictional cases against a live language model, inspect evidence IDs and follow-up questions, and compare results with human-authored reference labels.

The studio also manages go-live conditions, learning checks, approval invalidation, intervention records, revision conflicts, handover readiness and JSON evidence export.

## What is implemented

- **FastAPI** backend with rule-based transitions, input validation and versioned workspace records.
- **Neon PostgreSQL** for the hosted app and SQLite for local development. Workspace actions are transactional; stale revisions fail rather than overwrite newer changes.
- **Original responsive HTML/CSS/JavaScript** landing experience, workbench and configuration clinic.
- **A real Gemini API integration**, currently configured for `gemini-3.1-flash-lite`. The API key is server-side; no browser credential is exposed. The model returns structured observations for six fictional evidence scenarios. Returned evidence IDs are checked against the supplied fixtures.
- **Instruction-version history and provenance**: the record stores the configured instructions, model, version, timestamp, token usage and result. Agreement is measured against fixed human-authored labels.
- **Bounded public inference**: three calls per anonymous workspace and twelve calls globally per UTC day; failed calls count. No automatic paid-provider fallback.

## What the evaluation does **not** establish

Six fictional cases do not establish model accuracy, fairness, bias-free decisions or commercial return. A validated citation ID is not proof that a model interpreted the cited text correctly. The synthetic mapping test is not an external ATS connection. Self-recorded training and approval entries are not authenticated client actions. There is no real customer rollout, live recruiting data, or hiring recommendation.

The site uses an anonymous, randomly generated workspace cookie rather than a user login. It is a low-volume portfolio demonstration, not a production recruitment or compliance system. Free-tier availability and prices depend on the API project's actual Google billing status, not the application alone. Do not enter real personal or applicant information.

## Run locally

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
python -m uvicorn server:app --reload
```

Open `http://127.0.0.1:8000`. SQLite persistence works without a cloud account. To enable live inference, configure `GEMINI_API_KEY` **privately on the server** using a Google project with the desired billing restrictions. For Vercel hosting, configure `DATABASE_URL` with a separate PostgreSQL database.

## Verify

```bash
python -m pytest -q
python tests/browser_smoke.py
python tests/experience_smoke.py
python tests/ai_browser_smoke.py
```

The tests include local persistence, approval invalidation, mapping failure and recovery, adoption rules, isolation, optimistic revision conflicts, malformed/citation-invalid model responses and mocked provider-output paths. Mocked model tests do **not** establish access to the live provider. Deployment status and actual model calls must be checked separately.

See [the demo walkthrough](docs/DEMO_GUIDE.md), [model operations](docs/AI_RELEASE_GATE.md), and [release verification](docs/RELEASE_AUDIT.md).

## Development note

Built with AI-assisted coding and iterative functional testing. The repository records the implementation, tests and limitations; it should not be interpreted as evidence of unaided programming or experience deploying Metaview for customers.

## Reference material

The fictional scenario was informed by public information about AI recruiting configuration, implementation and adoption:
- [Metaview — Implementation Specialist](https://jobs.ashbyhq.com/metaview/846deb54-759a-4486-9e31-f4cde42dce91)
- [Metaview — case studies](https://www.metaview.ai/resources/case-study)

These references are context, not endorsements or evidence of a customer relationship.
