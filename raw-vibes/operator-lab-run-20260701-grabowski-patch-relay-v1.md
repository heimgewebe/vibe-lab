# Operator-Lab Run: Grabowski Patch Relay v1

Date: 2026-07-01
Target repo: heimgewebe/grabowski
Operation: optimize Operator Relay v0 so local bounded patch application replaces user manual patch downloads where possible.

Trigger check:
- PR-/Agentenlauf? yes
- starker Claim möglich? yes
- Run Card nötig? yes

Hypothesis:
A local patch relay can check/apply a patch file against a repo/head and write a receipt, making manual user patch execution the last fallback rather than the standard path.

Planned evidence:
- Add bounded helper in Grabowski.
- Add tests for check, apply, dirty repo rejection, and expected-head rejection.
- Reference this run in the Grabowski PR body.

Non-goals:
- no automatic merge
- no automatic push
- no automatic deploy
- no remote patch ingestion
