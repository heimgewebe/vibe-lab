---
title: "Blueprint v2 — Delta"
status: active
canonicality: operative
created: "2026-04-15"
updated: "2026-04-15"
relations:
  - type: derived_from
    target: ../concepts/execution-bound-epistemics.md
  - type: informs
    target: ../masterplan.md
  - type: references
    target: ../../schemas/experiment.manifest.schema.json
  - type: references
    target: ../../schemas/run_meta.schema.json
  - type: references
    target: ../../schemas/decision.schema.json
---

# Blueprint v2 — Delta

Dies ist **kein** Zielbild und **keine** neue Architektur. Zielbild steht in
`docs/foundations/vision.md`, Prinzipien in `docs/masterplan.md`, Semantik in
`docs/concepts/execution-bound-epistemics.md`. Dieses Dokument beschreibt **nur**
das operative Delta von v1 nach v2: welche **benannten Fehlklassen** mit welchen
**minimalen Hebeln** geschlossen werden, und wo bewusst **nicht** eingegriffen wird.

Struktur pro Abschnitt: **Fehlklasse → Hebel → minimale Änderung → Nicht-Ziel.**

---

## Phase 1 (aktiv) — Execution-Proof

**Fehlklasse:** Ein Manifest deklariert `execution_status: executed` oder
`replicated`, ohne dass ein erfasster Run-Beleg existiert.
Semantisch bereits definiert (`execution-bound-epistemics.md §5.2`), aber bisher
nicht erzwungen.

**Hebel:** Artefaktgebundene Pflicht statt Zusatzfeld.

**Minimale Änderung:**
- `schemas/run_meta.schema.json` (neu): Pflichtfelder `schema_version`, `run_id`,
  `generated_at`, `executor`, `command`, `exit_code`, `test_output_file`,
  `provenance_level`.
- `scripts/docmeta/validate_execution_proof.py` (neu): bei
  `execution_status ∈ {executed, replicated}` muss mindestens eine
  `artifacts/<run-id>/run_meta.json` existieren, schema-valide sein, und das
  referenzierte `test_output_file` muss innerhalb des Experiment-Roots existieren.
- CI-Step in `.github/workflows/validate.yml` nach `validate_schema.py`.

**Nicht-Ziel:** Kein eigenes neues Manifest-Feld für Run-Nachweise — das
bestehende `execution_refs` bleibt. Kein Zwang, den Run automatisiert zu
replizieren.

---

## Phase 1 (aktiv) — Adoption-Basis sichtbar machen

**Fehlklasse:** Ein Experiment wird als `status: adopted` geführt, obwohl kein
Execution-Proof vorliegt. Adoption erscheint ungeprüft, weil die Grundlage nicht
im Manifest steht.

**Hebel:** Lokale Deklaration im Manifest, keine zentrale Allowlist.

**Minimale Änderung:**
- `schemas/experiment.manifest.schema.json`: neues Feld `adoption_basis`
  (Enum: `executed` | `replicated` | `reconstructed`). **Pflicht** bei
  `status: adopted` (conditional `if/then`). Bei `adoption_basis: reconstructed`
  prüft der Validator zusätzlich, dass `results/result.md` die Marker-Zeichenkette
  `adoption_basis: reconstructed` enthält (sichtbare Annotation).
- `execution_status`-Enum wird um `reconstructed` erweitert
  (gem. `execution-bound-epistemics.md §11.1`), um historische Einstufung ohne
  erfassten Run auszusprechen, statt sie still zu tolerieren.

**Nicht-Ziel:** Keine zentrale Ausnahmeliste. Jede rekonstruktive Adoption steht
lokal am Experiment, nicht versteckt im Validator.

---

## Übergangsregel Altbestand

`adoption_basis: reconstructed` ist für **historische** Experimente zulässig,
aber kein Goldstandard. Neue Adoptionen — definiert als Experimente mit
`created` ≥ Merge-Datum dieses v2-PRs — müssen
`adoption_basis ∈ {executed, replicated}` tragen.

> Adoption ohne Execution-Proof ist nur als historischer Zustand zulässig,
> nicht als zukünftiger.

**Enforcement:** Seit Phase 1b hartes Enforcement in
`validate_execution_proof.py`: `adoption_basis: reconstructed` bei
`created ≥ v2-Merge-Datum` → **Fehler**. Gemeinsam mit Decision-Type-Separation
umgesetzt — selbe Fehlklasse (unberechtigte Adoption).

**Migration beim Einführen von v2 (einmalig, abgeschlossen):** `spec-first` →
`reconstructed` + Annotation; `yolo-vs-spec-first` → `designed`;
`spec-first-legacy` → `executed` mit nachgereichter `run_meta.json`.

---

## Phase 1b (aktiv) — Decision-Type + Übergangsregel-Enforcement

**Fehlklasse:** `execution-bound-epistemics.md §10.1–10.2` definiert drei
Assessment-Typen mit harter Regel „`adoption_assessment` nur bei
`executed`/`replicated`" — vor Phase 1b nicht erzwungen.

**Hebel:** Typisierung + cross-file-Bedingung statt zentraler Allowlist.

**Minimale Änderung:**
- `schemas/decision.schema.json` (neu): Diskriminator `decision_type`
  (`execution_assessment` | `result_assessment` | `adoption_assessment`), pro
  Typ eigene `verdict`-Enum und Pflichtfelder.
- `validate_decision_files()` + `validate_adoption_decision_coverage()` in
  `validate_schema.py` erzwingen die Kopplung **symmetrisch**:
  (a) `adoption_assessment` verlangt im Manifest `execution_status ∈
  {executed, replicated}`; (b) umgekehrt verlangt ein Manifest mit
  `status: adopted` + `adoption_basis ∈ {executed, replicated}` ein
  `adoption_assessment`. Ausnahme: `adoption_basis: reconstructed`.
- `validate_execution_proof.py`: `adoption_basis=reconstructed` bei
  `created ≥ v2-Merge-Datum` → **Fehler** (zuvor Warnung).
- Migration: alle sieben bestehenden `decision.yml` (inkl. Template) tragen
  `decision_type`; `prompt-length-control` bekommt das fehlende `decision.yml`
  als `adoption_assessment` nachgezogen.

**Nicht-Ziel:** Verdict-Enums über die drei Adoption-Verdicts
(`adopt` / `reject` / `defer`) hinaus ausbauen, bevor ein echtes
Execution-Review-Experiment geschrieben wird.

---

## Phase 2 (konditional) — Interpretation Protection

**Fehlklasse:** Ergebnisse werden über die tatsächliche Evidenzbasis hinaus
gelesen (überdehnte Claims, implizite Kausalbehauptungen).

**Hebel:** Schmale Anforderung, **nur** bei Promotion oder Regelbildung.

**Minimale Änderung:** `interpretation_budget` (Blöcke `allowed_claims` /
`disallowed_claims`) im `result.md`. Optionaler „Epistemic Stress Test"-Abschnitt
im Template.

**Nicht-Ziel:** Pflicht für alle Experimente. Exploration bleibt frei.

---

## Phase 3 (konditional) — Method Calibration

**Fehlklasse:** Vergleichsexperimente ohne explizite Confound-Isolation;
Adoptions-Entscheidungen ohne Metrik-Basislinie.

**Hebel:** Claim-gebundene Pflicht.

**Minimale Änderung:** `metrics.md` Pflicht nur bei `adoption_basis ∈ {executed,
replicated}` **und** expliziten Vergleichsexperimenten; Confound-Isolation-Sektion
in `method.md` nur dort.

**Nicht-Ziel:** `comparison_mode`-Enum (premature formalization — erst einführen,
wenn das zweite echte Vergleichsexperiment geschrieben wird; bis dahin reicht
freies `comparison_notes` in `method.md`).

---

## Derived Visibility — `epistemic_state` als Report

**Fehlklasse:** Manifest-Felder (`execution_status`, `evidence_level`,
`adoption_basis`) sind korrekt, aber schwer als Gesamtbild zu lesen.

**Hebel:** Generierte Sichtbarkeitsebene, **kein** Autorfeld.

**Minimale Änderung (Form, Implementierung offen):** Generator unter
`docs/_generated/` erzeugt pro Experiment einen abgeleiteten
`epistemic_state`-Report. Felder sind **derived**, nicht im Manifest dupliziert:
`design_quality` (aus `method.md`/`failure_modes.md`), `execution_state`
(Spiegel), `evidence_strength` (Spiegel), `interpretation_risk` (einziges
echtes Neu-Feld; aus `result.md` bzw. Phase 2).

**Nicht-Ziel:** Neue Pflichtfelder im Manifest. Keine doppelte Wahrheit.

---

## Nicht-Ziele von v2 (zusammengefasst)

- **`comparison_mode`-Enum.** Empirisch noch nicht gedeckt.
- **Zentrale Allowlist für Altbestand.** Allowlists wachsen, Lokalannotation nicht.
- **Meta-Lernschicht / `failure-atlas/`.** Dormant bis ≥ 3 dokumentierte Fehlklassen vorliegen.
- **`expected_outputs.json` als Pflicht.** Post-Blueprint, nicht jetzt.

---

## Verifikation

1. `python3 scripts/docmeta/validate_schema.py` grün (inkl. `decision.yml`-Zone).
2. `python3 scripts/docmeta/validate_execution_proof.py` grün.
3. Negativtests (lokal, nicht committen) — jeder muss fehlschlagen:
   `execution_status: executed` ohne `run_meta.json`; `status: adopted` ohne
   `adoption_basis`; `decision_type: adoption_assessment` bei
   `execution_status ∈ {designed, reconstructed}`; `adoption_basis: reconstructed`
   bei `created ≥ v2-Merge-Datum`; `status: adopted` + `adoption_basis: executed`
   mit `decision_type: result_assessment` (Gegenrichtung).
4. `make validate` grün.
