---
title: "Experiment-Ergebnis: Generated Artifact Contract Validation"
status: draft
canonicality: operative
---

# result.md — Experiment-Ergebnis

## Zusammenfassung

**Stand nach PR-58 (vollständig, mit Folge-Commits):** Ein realer PR-Run (Run-001) ist dokumentiert. Ein zweiter PR-Run (Run-002) existiert noch nicht — die Hypothese ist noch nicht hypothesenprüfbar.

Neben Run-001 wurden drei In-PR-Beobachtungen auf PR-58 gemacht, die direkt zur CI-Friction-Messung beitragen: der canonical generator produzierte innerhalb desselben PRs zweimal nicht-deterministische Ausgabe (path resolution bug, .venv-Leck), was drei Regenerationsläufe des canonical artifacts `doc-index.md` innerhalb eines einzigen PRs auslöste.

## Beobachtungen

> Gestützt auf evidence.jsonl. Keine Schlüsse hier — die gehören in ## Deutung.

### Wirksamkeit (Effektivität)
Die Klassentrennung `canonical/derived/ephemeral` ist im PR-Diff auswertbar. In PR-58 waren betroffen:
- 2 canonical (docs/_generated/doc-index.md, docs/_generated/system-map.md)
- 1 derived (docs/_generated/orphans.md)
- 1 ephemeral (docs/_generated/epistemic-state.md)

Wirksamkeitsmessung im Sinne der Hypothese (Reduktion von CI-Friction) ist auf Basis eines Runs noch nicht möglich.

### Reibung (Aufwand)
Folgende Reibungspunkte wurden innerhalb PR-58 beobachtet (nicht als separater Run — In-PR-Beobachtungen):

- **Commit d561893** (Apr 19, 10:27): Canonical artifact `doc-index.md` und `system-map.md` wurden ein zweites Mal regeneriert nach einem Bug in `resolve_generated_artifact_paths.py`.
- **Commit 7c44b07** (Apr 19, 10:52): Canonical artifact `doc-index.md` wurde ein drittes Mal regeneriert. Ursache: `.venv`-Verzeichnis wurde vom canonical generator fälschlicherweise gescannt (doc count: 122 statt 120). Fix durch Ausschluss von `.venv` und `venv` in `_paths.py`.
- Beide Fälle belegen reale manuelle Nacharbeit (Bugfix + Regen) für canonical artifacts innerhalb eines PRs.
- `ci_blocking_failures` und `manual_regen_steps` als vollständige Metriken: **nicht gemessen** (kein CI-Log-Zugriff, keine explizite Zählung der Regen-Commands).

### Diagnosis Clarity
`diagnosis_clarity_score`: **nicht gemessen**. Die Quelle der Nicht-Determinismus-Bugs war im Nachhinein über die Commit-Messages nachvollziehbar, aber nicht über das CI-System beobachtet.

## Deutung

> Interpretation, explizit als solche markiert.

Die beobachteten Reibungspunkte (drei Regen-Zyklen eines canonical artifacts in einem PR) könnten auf unzureichende Tooling-Stabilität des Generators hindeuten — aber das ist Interpretation auf Basis eines einzigen PRs. Belastbare Aussagen über Friction-Reduktion gegen Baseline setzen mindestens Run-002 voraus.

Die Klassentrennung canonical/derived/ephemeral macht Drift im Diff auswertbar — das ist eine Beobachtung. Ob sie CI-Friction reduziert, ist noch nicht messbar.

## Verdict

Offen. Execution begonnen (Run-001 + In-PR-Beobachtungen). Hypothesenprüfung erfordert mindestens Run-002 unter neuem Contract-System mit vollständiger Metrikerhebung.

## Lessons Learned

- Canonical artifacts erwiesen sich als anfälliger als erwartet: generator-bugs (path resolution, .venv-leak) lösten mehrfache Regenerationszyklen innerhalb eines PRs aus.
- `ci_blocking_failures` und `manual_regen_steps` sind die kritischsten Metriken, wurden aber in Run-001 nicht vollständig gemessen.
- Metrikerhebung muss für Run-002 explizit vorbereitet werden (CI-Log-Zugriff, explizite Regen-Zählung).

## Nächste Schritte

- Run-002 unter neuem echten PR erfassen (kein weiterer Push auf PR-58)
- CI-Statuschecks und manuelle Eingriffe per Run protokollieren
- `ci_blocking_failures`, `manual_regen_steps`, `diagnosis_clarity_score` vollständig erheben
- Danach: Wechsel auf `result_assessment` in `decision.yml` prüfen

## Interpretation Budget

> Pflicht bei adopted status / promotion-relevanten Experimenten. Wird befüllt vor Promotion.

### Allowed Claims
- Die Klassentrennung canonical/derived/ephemeral ist im PR-Diff beobachtbar und auswertbar (belegt durch Run-001, PR-58).
- In PR-58 wurden canonical artifacts mehrfach (3x) regeneriert — beobachtet, nicht quantitativ ausgewertet.

### Disallowed Claims
- Dass das Contract-Modell CI-Friction reduziert (nicht gemessen, kein Baseline-Vergleich).
- Verallgemeinerungen über "den PR-Prozess" auf Basis eines einzigen Runs.
- Adoption-Empfehlungen vor Run-002 + Hypothesenprüfung.

### Evidence Basis
- Direkt beobachtet: Run-001 (PR-58), Diff-Klassifikation, In-PR canonical regen × 3 (commits d561893, 7c44b07)
- Nicht gemessen: CI-blocking-failures, manual_regen_steps (explizit), diagnosis_clarity_score, baseline PRs
- Indirekt gestützt:
- Nicht getestet:
