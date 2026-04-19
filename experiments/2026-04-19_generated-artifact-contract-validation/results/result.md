---
title: "Experiment-Ergebnis: Generated Artifact Contract Validation"
status: draft
canonicality: operative
---

# result.md — Experiment-Ergebnis

## Zusammenfassung

**Stand nach PR-58 und PR-61:** Zwei reale PR-Runs sind dokumentiert. Run-001 liegt auf PR-58, Run-002 liegt als unabhaengiger PR-Run auf PR-61 vor. Die Evidenzlage ist klarer, aber fuer eine belastbare Hypothesenbewertung weiterhin noch nicht ausreichend.

Neben Run-001 wurden auf PR-58 zwei zusätzliche In-PR-Friction-Beobachtungen gemacht: der canonical generator produzierte innerhalb desselben PRs zweimal nicht-deterministische Ausgabe (path resolution bug, .venv-Leck). Zusammen mit dem initialen Run-001-Zustand ergeben sich mindestens drei canonical-Regenerationszustände für `doc-index.md` innerhalb eines einzigen PRs.

Die frühere Verfügbarkeitslücke ist geschlossen: Run-002 ist nun als unabhängiger PR-Run mit Artefakten (`artifacts/run-002-pr61/*`) belegbar.

## Beobachtungen

> Gestützt auf evidence.jsonl. Keine Schlüsse hier — die gehören in ## Deutung.

### Wirksamkeit (Effektivität)
Die Klassentrennung `canonical/derived/ephemeral` ist im PR-Diff auswertbar. In PR-58 waren betroffen:
- 2 canonical (docs/_generated/doc-index.md, docs/_generated/system-map.md)
- 1 derived (docs/_generated/orphans.md)
- 1 ephemeral (docs/_generated/epistemic-state.md)

Zusätzliche Reibungsbeobachtungen in diesem Fortschritt betreffen bisher nur canonical-Artefakte.

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

Die beobachteten Reibungspunkte (drei Regen-Zyklen eines canonical artifacts in PR-58 sowie ein blockierender CI-Fehler mit Fix-Zyklus in PR-61) deuten auf reale Prozessfriktion hin. Das bleibt jedoch Interpretation bei noch schmaler Vergleichsbasis.

Die Klassentrennung canonical/derived/ephemeral macht Drift im Diff auswertbar — das ist weiterhin beobachtbar. Ob sie CI-Friction reduziert, ist noch nicht robust quantifizierbar.

## Verdict

Vorläufig offen. Execution ist jetzt mit zwei unabhängigen PR-Runs belegt (Run-001/PR-58 und Run-002/PR-61). Ein finaler Hypothesenentscheid bleibt bis zu einer weiteren vergleichbaren Messung mit stabiler Baseline vertagt.

## Lessons Learned

- Canonical artifacts erwiesen sich als anfälliger als erwartet: generator-bugs (path resolution, .venv-leak) lösten mehrfache Regenerationszyklen innerhalb eines PRs aus.
- `ci_blocking_failures` und `manual_regen_steps` sind die kritischsten Metriken, wurden aber in Run-001 nicht vollständig gemessen.
- Run-002 hat gezeigt, dass die Metrikerhebung bei CI-Fehlern und Fix-Zyklen praktisch umsetzbar ist, aber die Vergleichsbasis bleibt schmal.

## Nächste Schritte

- Run-002-Konsolidierung sauber halten: Manifest, Decision und Result auf denselben Stand referenzieren
- Für den nächsten Run dieselbe Scope-Klasse beibehalten (eine Quelländerung + Generator-Interaktion)
- Metriken pro Run weiter strikt erfassen (`ci_blocking_failures`, `manual_regen_steps`, `diagnosis_clarity_score`)
- Danach: Wechsel auf `result_assessment` in `decision.yml` erneut prüfen

## Interpretation Budget

> Pflicht bei adopted status / promotion-relevanten Experimenten. Wird befüllt vor Promotion.

### Allowed Claims
- Die Klassentrennung canonical/derived/ephemeral ist im PR-Diff beobachtbar und auswertbar (belegt durch Run-001, PR-58).
- In PR-58 wurden canonical artifacts mehrfach (3x) regeneriert — beobachtet, nicht quantitativ ausgewertet.

### Disallowed Claims
- Dass das Contract-Modell CI-Friction reduziert (nicht gemessen, kein Baseline-Vergleich).
- Verallgemeinerungen über "den PR-Prozess" auf Basis eines einzigen Runs.
- Adoption-Empfehlungen vor zusätzlicher Vergleichsmessung und belastbarer Hypothesenprüfung.

### Evidence Basis
- Direkt beobachtet: Run-001 (PR-58), Diff-Klassifikation, In-PR canonical regen × 3 (commits d561893, 7c44b07)
- Nicht gemessen: CI-blocking-failures, manual_regen_steps (explizit), diagnosis_clarity_score, baseline PRs
