---
title: "Method: Operator Intervention Effect Evaluator"
status: active
canonicality: operative
---

# Method

1. Register one intervention before observations are collected.
2. Freeze control, treatment, primary metric, direction, material threshold, comparison mode, confounders, review date and expiry.
3. Collect only evidence-bound numeric observations.
4. Refuse unmatched pairs, mismatched comparison-key distributions, insufficient samples or missing independent observation.
5. Calculate the favorable effect and a deterministic 95 percent Student-t interval; unpaired comparisons use a conservative smaller-arm degree of freedom.
6. Emit only `beneficial`, `no_material_effect`, `harmful` or `insufficient_evidence`.
7. Compare the report with an independent manual decision. The report never applies a policy or route change.
