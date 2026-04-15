# Pre-Mortem Quality Evaluation (Run 008 Holdout)

- antizipierte_failure_pfade: 8
- relevante_failure_pfade_im_testset: 10
- explizit_getroffene_pfade: 8
- holdout_blindspots: 2 (`negative_price`, `zero_qty`)

## Metriken

- in_set_precision: 1.00
- full_suite_recall: 0.80
- global_anticipation_coverage: 0.80

Hinweis: `in_set_precision` ist innerhalb antizipierter Pfade hoch, aber Holdout-Blindspots bleiben sichtbar.
