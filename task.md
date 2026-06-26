# Filename: task.md

A small medical triage package was refactored and now behaves incorrectly.

Your job is to repair the repository so that the medical triage pipeline is internally consistent:

1. Valid inputs are triaged consistently.
2. Escalation is uncertainty-aware, not just based on raw risk.
3. Unsupported inputs are routed to a safe fallback.
4. Producing a summary is read-only and does not mutate patient state.

You may edit files under `src/triage/`.
Do not modify the tests or verifier code.

Success requires:
- correct triage behavior across low, moderate, and high-risk cases,
- escalation decisions that remain consistent with uncertainty-aware risk scoring,
- read-only summary generation that does not mutate patient state.