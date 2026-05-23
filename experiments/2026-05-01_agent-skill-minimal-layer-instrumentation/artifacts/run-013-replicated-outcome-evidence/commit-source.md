# Commit Source Snapshot

PR reference: https://github.com/heimgewebe/vibe-lab/pull/201
Capture timestamp: 2026-05-23T07:25:00Z

Command used:
- gh PR snapshot: `gh pr view 201 --json number,title,url,updatedAt,createdAt,state,reviewDecision,reviews,comments,commits,files`

Captured review timestamp used for rework classification:
- 2026-05-23T06:25:45Z (`review id: PRR_kwDOR8ZYIc8AAAABA0cJiQ`)

Captured commit set:
- 12d26c6d6b7503d80f90e450a54fbd6b011ac535
  - committed_at: 2026-05-23T05:02:24Z
  - relation_to_review: before
  - explicit_review_link: no
- 34ce0055c7a52f6f395dd6195a2eeeee6f0dbf52
  - committed_at: 2026-05-23T05:30:57Z
  - relation_to_review: before
  - explicit_review_link: no
- ce3ed367257f54f3f4d969684ef8222eefa21788
  - committed_at: 2026-05-23T05:37:28Z
  - relation_to_review: before
  - explicit_review_link: no
- bbf68756d3eb5900dd7c79fea60302522ea59db3
  - committed_at: 2026-05-23T05:45:46Z
  - relation_to_review: before
  - explicit_review_link: no
- 2efac086d6831721fb933ec8e325b9213798eb0e
  - committed_at: 2026-05-23T06:12:53Z
  - relation_to_review: before
  - explicit_review_link: no

Classification result:
- initial_task_brief_commit: 12d26c6d6b7503d80f90e450a54fbd6b011ac535
- revision_commit_count: 4 follow-up refinement commits after the initial task brief commit.
- counted_revision_commits:
  - 34ce0055c7a52f6f395dd6195a2eeeee6f0dbf52
  - ce3ed367257f54f3f4d969684ef8222eefa21788
  - bbf68756d3eb5900dd7c79fea60302522ea59db3
  - 2efac086d6831721fb933ec8e325b9213798eb0e
- review_driven_rework_count: not proven from captured evidence.
- Interpretation: rework_count follows the repo contract definition
  (follow-up commits revising prior claims). review_driven_rework_count is a stricter
  non-contract interpretation and must not replace rework_count.

Interpretation limit:
This is a repo-local point-in-time commit snapshot. It supports revision activity
observability and rework_count metric capture, but does not independently prove
review-driven causal linkage or outcome improvement.
