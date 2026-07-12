---
title: "Method: Operator Intervention Effect Evaluator"
status: active
canonicality: operative
---

# Method

1. Register one intervention before observations are collected.
2. Freeze control, treatment, primary metric, direction, material threshold, comparison mode, confounders, review date and expiry.
3. Randomize decision order and hide condition labels from the independent scorer; record any blinding failure instead of treating the pair as comparable.
4. The scorer applies the frozen four-component binary scorecard to each decision; the capture tool derives the numeric value and forbids a free score.
5. Measure total handling effort in seconds from condition preparation until the decision and scorecard are sealed, including evaluator report generation when applicable.
6. Capture each observation with `capture_effect_observation.py`; bind the aggregate to the exact registration digest and each evidence item to SHA-256.
7. Reject duplicate observation IDs, evidence references, evidence digests, out-of-scope output paths, post-expiry observations and concurrent lost updates.
8. Refuse unmatched pairs, mismatched comparison-key distributions, unblinded scoring, insufficient samples, self-scoring or the same decision maker on both sides of a pair.
9. Calculate the favorable effect and a deterministic 95 percent Student-t interval; unpaired comparisons use a conservative smaller-arm degree of freedom.
10. Report control and treatment effort separately without inventing a cost-effectiveness threshold.
11. Emit only `beneficial`, `no_material_effect`, `harmful` or `insufficient_evidence` for the registered primary effect.
12. Compare effect, measured effort and the independent manual decision during closure. The report never applies a policy or route change.
