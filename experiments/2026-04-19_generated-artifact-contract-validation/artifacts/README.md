# artifacts/

Hier landen Run-Artefakte für Experimente mit `execution_status ∈ {executed, replicated}`.

Struktur:

```
artifacts/
  <run-id>/
    run_meta.json       # Pflicht — Execution-Proof-Contract
    <test_output_file>  # Die in run_meta.json referenzierte Log-/Ergebnisdatei
```

`run_meta.json` wird gegen `schemas/run_meta.schema.json` validiert (siehe
`scripts/docmeta/validate_execution_proof.py`). `run_id` muss mit dem Ordnernamen
übereinstimmen; `test_output_file` muss als Datei existieren und innerhalb des
Experiment-Roots liegen.

Siehe `docs/blueprints/blueprint-v2.md` und `docs/concepts/execution-bound-epistemics.md §5.2`.
