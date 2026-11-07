# LaunchLab — a 90-second implementation walkthrough

1. **Command room:** Open Northstar Labs and notice the launch blockers. The initial state has **seven** open blockers. All data is fictional.
2. **Configure:** Edit **Strong communication** into an observable requirement, such as “Explains customer implementation blockers clearly with reproducible evidence and next steps.” Click **Review**, then record fictional hiring-owner approval.
3. **Go-live gates:** In **Field mapping lab**, set `job_id` to `job.invalid` and click **Run schema test**. Watch mapping fail. Restore `job.id`, rerun and see a real, validated transformed sample record (`JOB-231`, `SYN-104`, etc.). Record the two remaining fictional integration dry-runs with notes.
4. **Enablement:** Complete the hiring-manager and talent-operations learning checks with descriptive evidence. Set recruiter attendance to **4**, manager attendance to **2**, leaving operations at **1**.
5. **Go-live gates:** The deterministic readiness engine now permits a fictional pilot launch. Click **Launch synthetic pilot**.
6. **Adoption & recovery:** See week-one **4/11** active users. Record an intervention for the hiring-manager group; counts remain unchanged. Record fictional week-two activity as **5 recruiters, 2 managers, 1 talent-ops**. The target becomes **8/11**, but only because fresh synthetic usage evidence was entered.
7. **Handover:** View the generated memo and record a synthetic handover. Export the full evidence JSON. Reload the page; everything remains saved in this browser workspace.

**Do not mistake the simulated customer story for actual Metaview usage or real customers.** This case proves local application behaviour, not production software integrations or ROI.
