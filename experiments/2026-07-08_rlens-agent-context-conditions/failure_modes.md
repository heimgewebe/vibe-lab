---
title: "Failure Modes — rLens Agent Context Conditions"
status: designed
canonicality: operative
---

# Failure Modes — rLens Agent Context Conditions

| Failure mode | Effect | Mitigation |
| --- | --- | --- |
| Task difficulty dominates condition | Condition comparison becomes non-attributable | Record task class, PR size, changed files, domain context, and validation possibility. |
| Full dump increases fluent hallucination | Agent cites plausible but nonexistent paths or stale facts | Code `hallucinated_path_count` and `stale_context_claim_count`; do not promote full dump by default. |
| Trace gate adds too much ceremony | Evidence quality improves but total effort worsens | Track preparation, review, and correction time separately. |
| Derived context treated as truth | Agent trusts rLens navigation over live repo/PR evidence | Require live source verification for claim acceptance. |
| Reviewer learning confounds order | Later runs look better because the operator learned | Rotate conditions where possible and mark repeated task domains. |
| Mixed context contaminates run | Condition is no longer interpretable | Record allowed/disallowed context and invalidate contaminated runs. |
| Privacy boundary breach | External-safe condition receives raw/private context | Use context-pack only; record export boundary and redaction status. |
