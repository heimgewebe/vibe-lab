---
title: "Experiment-Ergebnis: Generated Artifact Contract Validation"
status: draft
canonicality: operative
---

# result.md — Experiment-Ergebnis

## Zusammenfassung

**Stand nach PR-58, PR-61 und PR-62:** Drei reale PR-Runs sind dokumentiert. Run-001 liegt auf PR-58, Run-002 als unabhängiger PR-Run auf PR-61, Run-003 als unabhängiger PR-Run auf PR-62.

Neben Run-001 wurden auf PR-58 zwei zusätzliche In-PR-Friction-Beobachtungen gemacht: der canonical generator produzierte innerhalb desselben PRs zweimal nicht-deterministische Ausgabe (path resolution bug, .venv-Leck). Zusammen mit dem initialen Run-001-Zustand ergeben sich mindestens drei canonical-Regenerationszustände für `doc-index.md` innerhalb eines einzigen PRs.

Run-003 (PR-62) war der erste saubere End-to-End-Lauf: keine CI-Blocking-Failures vor dem ersten Push, kein Fix-Zyklus im initialen Lauf, Determinismus bestätigt.

## Beobachtungen

> Gestützt auf evidence.jsonl. Keine Schlüsse hier — die gehören in ## Deutung.

### Wirksamkeit (Effektivität)
Die Klassentrennung `canonical/derived/ephemeral` ist im PR-Diff auswertbar. In PR-58 waren betroffen:
- 2 canonical (docs/_generated/doc-index.md, docs/_generated/system-map.md)
- 1 derived (docs/_generated/orphans.md)
- 1 ephemeral (docs/_generated/epistemic-state.md)

In PR-62 waren betroffen:
- 0 canonical (doc-index.md, system-map.md: unverändert)
- 1 derived (docs/_generated/orphans.md)
- 0 ephemeral

### Reibung (Aufwand)

**Run-001 / PR-58** (in-PR, nicht als separater Run):
- **Commit d561893**: Canonical artifact `doc-index.md` und `system-map.md` zweites Mal regeneriert nach Bug in `resolve_generated_artifact_paths.py`.
- **Commit 7c44b07**: `doc-index.md` drittes Mal regeneriert. `.venv`-Verzeichnis fälschlicherweise gescannt. Fix + Regen.
- `ci_blocking_failures`: nicht gemessen. `manual_regen_steps`: nicht gemessen.

**Run-003 / PR-62** (vollständig gemessen):
- `ci_blocking_failures`: 0
- `ci_non_blocking_warnings`: 0
- `manual_regen_steps`: 1 (erster generate-Lauf; zweiter war Determinismus-Check, idempotent)
- `unnecessary_commit_delta`: 0
- `diagnosis_clarity_score`: 5/5

### Diagnosis Clarity
Run-001: nicht gemessen. Run-003: 5/5 (sauber, keine Unklarheit über Fehlerursachen).

## Deutung

> Interpretation, explizit als solche markiert.

Der Kontrast zwischen Run-001 (mehrere Regenerationszyklen), Run-002 (ein blockierender CI-Fehler mit Fix-Zyklus) und Run-003 (initial sauberer Lauf) deutet auf sinkende Friction hin. Das bleibt Interpretation, weil Ursachenmix und Messdisziplin über die Runs noch nicht vollständig vereinheitlicht sind.

## Verdict

Vorläufig offen. Drei dokumentierte PR-Runs liegen vor, aber die Vergleichsbasis ist methodisch noch nicht stabil genug für einen belastbaren Hypothesenentscheid.

## Lessons Learned

- Canonical artifacts erwiesen sich in Run-001 als anfällig: generator-bugs lösten mehrfache Regenerationszyklen aus.
- Run-002 zeigte, dass CI-Fehler/Fix-Zyklen metrikfähig dokumentierbar sind.
- Run-003 war der erste initial saubere End-to-End-Lauf mit vollständiger Metrikerhebung.
- Die Determinismus-Prüfung (double-run check) ist reproduzierbar und schnell.

## Nächste Schritte

- Messdefinitionen über Run-001/Run-002/Run-003 harmonisieren (gleiches Feldset, gleiche Scope-Interpretation).
- Für den nächsten vergleichbaren Run dieselbe Scope-Klasse beibehalten (eine Quelländerung + Generator-Interaktion).
- Danach: Wechsel auf `result_assessment` in `decision.yml` erneut prüfen.

## Interpretation Budget

> Pflicht bei adopted status / promotion-relevanten Experimenten. Wird befüllt vor Promotion.

### Allowed Claims
- Die Klassentrennung canonical/derived/ephemeral ist im PR-Diff beobachtbar und auswertbar (belegt durch Run-001, PR-58 und Run-003, PR-62).
- In PR-58 wurden canonical artifacts mehrfach (3x) regeneriert — beobachtet, nicht quantitativ ausgewertet.
- In PR-62 wurden null CI-Blocking-Failures beobachtet und alle Metriken vollständig erhoben.
- Run-003 ist der erste vollständig metrik-erfasste saubere Lauf in diesem Experiment.

### Disallowed Claims
- Dass das Contract-Modell CI-Friction robust reduziert (keine harmonisierte Baseline, Ursachenmix über drei Runs).
- Verallgemeinerungen über "den PR-Prozess" ohne zusätzliche vergleichbare Messungen.
- Adoption-Empfehlungen ohne belastbare result_assessment-Entscheidung.

### Evidence Basis
- Direkt beobachtet: Run-001 (PR-58), Diff-Klassifikation, In-PR canonical regen × 3 (commits d561893, 7c44b07)
- Nicht gemessen: CI-blocking-failures, manual_regen_steps (explizit), diagnosis_clarity_score, baseline PRs
