# Filename: task.md

### Set up
`triage`, a small Python medical triage package was refactored and now behaves incorrectly.

### Objective
Your job is to repair the repository so that the triage pipeline is **internally consistent**, meaning:

1. Valid inputs are triaged consistently.
2. Escalation decisions are uncertainty-aware, not just based on raw risk.
3. Unsupported inputs are routed to a safe fallback.
4. The produced summary is read-only and does not mutate patient state.

### Rules
You may edit files under `src/triage/`.
Do not modify the tests or verifier code under `tests/` and `verifier/` respectively.

### Evaluation
A successful repair requires all of the following criteria:
- correct triage behaviour for cases across all risk levels;
- escalation decisions that remain consistent with uncertainty-aware risk scoring;
- safe fallback behaviour for out-of-range inputs; and
- read-only summary generation that does not mutate patient state.