---
title: "Blueprint v2 — Roadmap / offene Punkte"
status: active
canonicality: navigation
created: "2026-04-15"
updated: "2026-04-23"
triggered_by: "v2 roadmap: Derived Visibility — Sichtbarkeits-Kriterium erfüllt (10 Experimente ≥ 5)"
relations:
  - type: derived_from
    target: ./blueprint-v2.md
  - type: references
    target: ../concepts/execution-bound-epistemics.md
---

# Blueprint v2 — Roadmap / offene Punkte

Dies ist eine reine Verfolgungsliste. Keine neuen Prinzipien, keine neuen Regeln.
Nur: **was bewusst in Phase 1 nicht umgesetzt wurde**, **wofür**, und **woran
man den nächsten Schritt erkennt**.

Verankert in `blueprint-v2.md`. Jeder Eintrag nennt die Fehlklasse, den
geplanten Hebel und ein Sichtbarkeits-Kriterium, ab wann Umsetzung sinnvoll ist.

---

## Phase 2 — Interpretation Protection (Restoffen)

**Fehlklasse:** Der Kernschutz gegen Overclaiming ist umgesetzt; offen bleibt
die optionale Zusatzhärtung über einen expliziten epistemischen Stress-Test.

**Hebel:**
- Optionaler „Epistemic Stress Test"-Abschnitt im Template.

**Bewusst nicht mehr offen:** `interpretation_budget` als Promotion-Guard. Das
liegt bereits als Policy + Validator + Test + CI-Verkabelung im Repo.

**Sichtbarkeits-Kriterium:** Erst wenn die bestehende Guard-Flaeche in Reviews
nicht mehr reicht und ein zusaetzlicher Stress-Test echten Mehrwert liefert.

---

## Phase 3 — Method Calibration

**Fehlklasse:** Vergleichsexperimente ohne explizite Confound-Isolation;
Adoptions-Entscheidungen ohne Metrik-Basislinie.

**Hebel:**
- `metrics.md` Pflicht nur bei `adoption_basis ∈ {executed, replicated}` **und**
  expliziten Vergleichsexperimenten.
- Confound-Isolation-Sektion in `method.md` (gleiche Bedingung).

**Bewusst weggelassen:** `comparison_mode`-Enum. Erst einführen, wenn das
zweite echte Vergleichsexperiment geschrieben wird. Bis dahin freies
`comparison_notes`.

**Sichtbarkeits-Kriterium:** Zweites Vergleichsexperiment mit Adoptions-Anspruch.

---

## Dormant — Meta-Learning (`meta/failure-atlas/`)

**Aktivierung erst, wenn:** ≥ 3 dokumentierte Fehlklassen aus echten
Experimenten vorliegen. Bis dahin bewusst nicht anlegen.

---

## Nicht-Ziele (bleiben ausgeschlossen)

- **`comparison_mode`-Enum** — premature formalization, s. Phase 3.
- **Zentrale Allowlists** für Altbestand — Lokalannotation (`adoption_basis`)
  schlägt Liste.
- **`expected_outputs.json` als Pflicht** — post-blueprint.
- **Flächige Governance-Erweiterung** — jede neue Pflicht muss eine benannte
  Fehlklasse aus einem echten PR haben, sonst nicht.

---

## Erledigte Punkte (zum Nachlesen)

- **Phase 2 — Interpretation Protection (Kern):**
  `docs/policies/interpretation-budget.md` definiert den Pflichtblock fuer
  adoptierte Experimente; `validate_interpretation_budget.py` + Tests + CI
  erzwingen den Guard im Repo.

- **Phase 1 — Execution-Proof:** `schemas/run_meta.schema.json` +
  `scripts/docmeta/validate_execution_proof.py`, im CI verdrahtet.
- **Phase 1 — Adoption-Basis sichtbar:** Feld `adoption_basis` im Schema,
  pflichtig bei `status: adopted`, mit Konsistenzregel gegen `execution_status`.
  `execution_status`-Enum um `reconstructed` erweitert.
- **Phase 1 — Übergangsregel (weich):** Warnung bei
  `adoption_basis: reconstructed` ab `created ≥ 2026-04-15`.
- **Phase 1 — Altbestand-Migration:** spec-first (reconstructed, mit
  Annotation), yolo-vs-spec-first (designed), spec-first-legacy (executed
  mit run_meta.json).
- **Phase 1b — Decision-Type-Separation:** `schemas/decision.schema.json`
  mit Diskriminator `decision_type` (`execution_assessment` |
  `result_assessment` | `adoption_assessment`); cross-file Kopplung
  symmetrisch erzwungen in `validate_schema.py`: (a) `adoption_assessment`
  verlangt `execution_status ∈ {executed, replicated}`; (b) `status: adopted`
  + `adoption_basis ∈ {executed, replicated}` verlangt `adoption_assessment`.
  Historische Ausnahme `adoption_basis: reconstructed` bleibt.
- **Phase 1b — Übergangsregel (hart):** `adoption_basis: reconstructed` bei
  `created ≥ 2026-04-15` → **Fehler** (zuvor Warnung). Datumsvergleich via
  `datetime.date.fromisoformat()`, nicht lexikographisch.
- **Phase 1b — Format-Enforcement:** `validate_schema.py` nutzt uniform
  `Draft202012Validator` + `FORMAT_CHECKER`, damit `"format": "date"` in
  allen Schemas (manifest / catalog / combo / decision / docmeta) tatsächlich
  geprüft wird.
- **Derived Visibility — `epistemic_state`-Report:**
  `scripts/docmeta/generate_epistemic_state.py` erzeugt
  `docs/_generated/epistemic-state.md` mit abgeleiteten Feldern pro
  Experiment: `design_quality` (aus `method.md` / `failure_modes.md`),
  `execution_state` (Spiegel), `evidence_strength` (Spiegel),
  `interpretation_risk` (aus 6-Signal-Heuristik, nicht mehr `unassessed`).
  Sichtbarkeits-Kriterium erfüllt: 10 Experimente ≥ 5. Im Makefile als
  `generate-epistemic-state` verdrahtet.
