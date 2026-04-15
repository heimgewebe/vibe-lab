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
---

# Blueprint v2 — Delta

Dies ist **kein** Zielbild und **keine** neue Architektur. Zielbild steht in
`vision.md`, Prinzipien in `docs/masterplan.md`, Semantik in
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

**Enforcement:** In Phase 1 **nicht** als Validator-Check umgesetzt. Die
`created`-Datum-Regel wird zusammen mit Phase 1b (Decision-Type-Enforcement)
eingezogen, weil sie an derselben Fehlklasse arbeitet
(unberechtigte Adoption).

**Migration beim Einführen von v2 (einmalig):**
- `2026-04-08_spec-first` — `status: adopted` → `execution_status: reconstructed`,
  `adoption_basis: reconstructed`; sichtbarer Hinweis im `results/result.md`.
- `2026-04-11_yolo-vs-spec-first` — `status: designed` → `execution_status: designed`.
- `2026-04-12_spec-first-legacy` — `status: testing` → `execution_status: executed`
  (Testlauf-Artefakte existieren), `run_meta.json` nachgereicht.

---

## Phase 1b (nachgelagert, **nicht** in diesem PR) — Decision-Type + Übergangsregel-Enforcement

**Offene Restschuld.** `execution-bound-epistemics.md §10.1–10.2` definiert drei
Assessment-Typen mit harter Regel „`adoption_assessment` nur bei
`executed`/`replicated`" — aktuell nirgends erzwungen (`decision.yml` ist nur
Template). Execution-Proof schließt die gröbste Fälschungslücke;
Decision-Type bleibt die nächste offene Enforcement-Lücke.

**Geplanter Hebel (nicht hier):** `schemas/decision.schema.json` mit conditional
`adoption_assessment` → Manifest-`execution_status ∈ {executed, replicated}`.
Gleicher PR schließt dann auch den `created`-Datum-Check für die Übergangsregel.

**Nicht-Ziel jetzt:** Schema zweimal anfassen, bevor Phase 1 gelebt ist.

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

**Minimale Änderung (in Form beschrieben, **Implementierung offen**):** Ein
zukünftiger Generator unter `docs/_generated/` erzeugt pro Experiment einen
abgeleiteten `epistemic_state`-Report. Felder sind **derived**, nicht im Manifest
dupliziert:
- `design_quality` — abgeleitet aus Vollständigkeit von `method.md` / `failure_modes.md`
- `execution_state` — Spiegel von `execution_status`
- `evidence_strength` — Spiegel von `evidence_level`
- `interpretation_risk` — einziges echtes neues Feld; aus `result.md` extrahiert
  oder manuell ergänzt, wenn Phase 2 greift

**Nicht-Ziel:** Neue Pflichtfelder im Manifest. Keine doppelte Wahrheit.

---

## Nicht-Ziele von v2 (zusammengefasst)

- **`comparison_mode`-Enum.** Empirisch noch nicht gedeckt.
- **Zentrale Allowlist für Altbestand.** Allowlists wachsen, Lokalannotation nicht.
- **Vollständige Meta-Lernschicht / `failure-atlas/`.** Bleibt dormant bis ≥ 3
  dokumentierte Fehlklassen aus echten Experimenten vorliegen.
- **`expected_outputs.json` als Pflicht.** Post-Blueprint, nicht jetzt.
- **Decision-Type-Enforcement.** Phase 1b, nicht in diesem PR.
- **`created`-Datum-Check für Übergangsregel.** Zusammen mit 1b.

---

## Verifikation

1. `python3 scripts/docmeta/validate_schema.py` grün.
2. `python3 scripts/docmeta/validate_execution_proof.py` grün.
3. Negativtest (lokal, nicht committen): `execution_status: executed` ohne
   `run_meta.json` → Validator **muss** fehlschlagen. `status: adopted` ohne
   `adoption_basis` → Validator **muss** fehlschlagen.
4. `make validate` grün.
