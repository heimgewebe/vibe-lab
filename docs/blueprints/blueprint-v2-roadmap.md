---
title: "Blueprint v2 — Roadmap / offene Punkte"
status: active
canonicality: navigation
created: "2026-04-15"
updated: "2026-04-16"
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

## Phase 2 — Interpretation Protection

**Fehlklasse:** Ergebnisse werden über die Evidenzbasis hinaus gelesen
(überdehnte Claims, implizite Kausalbehauptungen).

**Hebel:**
- `interpretation_budget` (Blöcke `allowed_claims` / `disallowed_claims`) im
  `result.md`.
- Optionaler „Epistemic Stress Test"-Abschnitt im Template.

**Pflicht nur bei:** Promotion oder Regelbildung. Exploration bleibt frei.

**Sichtbarkeits-Kriterium:** Nach der ersten post-v2-Adoption, spätestens wenn
ein Reviewer ein adoptiertes Ergebnis überdehnt zitiert.

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

## Derived Visibility — `epistemic_state`-Report

**Fehlklasse:** Manifest-Felder korrekt, aber schwer als Gesamtbild zu lesen.

**Hebel:** Generator unter `scripts/docmeta/` der pro Experiment einen
abgeleiteten Report erzeugt. Felder `execution_state` / `evidence_strength` sind
Spiegel (nicht Autorfelder); `interpretation_risk` ist das einzige echte neue
Feld (greift Phase 2).

**Nicht-Ziel:** Manifest-Duplikation.

**Sichtbarkeits-Kriterium:** Wenn ≥ 5 Experimente existieren und ein manueller
Überblick erkennbar nicht mehr skaliert.

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
