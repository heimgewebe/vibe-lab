---
title: "Experiment-Ergebnis: Generated Artifact Contract Validation"
status: draft
canonicality: operative
---

# result.md — Experiment-Ergebnis

## Zusammenfassung

**Stand nach PR-58, PR-61, PR-62, PR-63, PR-64 und PR-67:** Sechs PR-Runs sind dokumentiert. Run-001 liegt auf PR-58, Run-002 als unabhängiger PR-Run auf PR-61, Run-003 als unabhängiger PR-Run auf PR-62, Run-004 als unabhängiger PR-Run auf PR-63, Run-005 als unabhängiger PR-Run auf PR-64, Run-006 als unabhängiger natürlicher clean_reference-Run auf PR-67.

Neben Run-001 wurden auf PR-58 zwei zusätzliche In-PR-Friction-Beobachtungen gemacht: der canonical generator produzierte innerhalb desselben PRs zweimal nicht-deterministische Ausgabe (path resolution bug, .venv-Leck). Zusammen mit dem initialen Run-001-Zustand ergeben sich mindestens drei canonical-Regenerationszustände für `doc-index.md` innerhalb eines einzigen PRs.

Run-003 (PR-62) war der erste saubere End-to-End-Lauf: keine CI-Blocking-Failures im initialen CI-Lauf, kein Fix-Zyklus, Determinismus bestätigt.

Run-004 (PR-63) wurde als bewusst leicht gestörter Lauf erfasst: eine kleine, kontrollierte Schema-Abweichung in `results/evidence.jsonl` erzeugte genau einen blockierenden Validate-Fehler und wurde in einem Fix-Schritt behoben.

Run-005 (PR-64) wurde als Kalibrierungslauf mit identischer kontrollierter Schema-Injektion ausgeführt. Die Friction blieb semantisch und lokal: ein blockierender Validate-Fehler, schnelle Lokalisierung, kurzer Fix-Zyklus bis wieder alle Checks grün waren.

Run-006 (PR-67) wurde als natürlicher clean_reference-Lauf ohne künstliche Friktion gestartet. Scope: eine kleine canonical Formulierungsänderung in `docs/foundations/vision.md`, danach deterministischer double-run mit `make generate`. Im PR trat dennoch einmal strukturelle Konsolidierungsfriktion auf (stale `system-map.md`), die mit einem einzelnen canonical-Regenerationscommit behoben wurde.

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

**Run-004 / PR-63** (kontrollierte Friction):
- `ci_blocking_failures`: 2 (1x schema validate, 1x canonical contract bei Konsolidierung)
- `manual_regen_steps`: 1
- `diagnosis_clarity_score`: 4/5
- `unnecessary_commit_delta`: 2
- Was schief lief: Schema-Verstoß in `results/evidence.jsonl` (fehlender required key `context`, line 31)
- Wie schnell erkannt: 47 Sekunden von erstem Failed-Timestamp bis expliziter Fehleridentifikation
- Schritte zur Behebung: 2 (fehlenden `context`-Key ergänzt; danach `system-map.md` per Generate regeneriert und committed)

**Run-005 / PR-64** (kalibrierte kontrollierte Friction):
- `ci_blocking_failures_total`: 2
- `manual_regen_steps`: 2
- `diagnosis_clarity_score`: 5/5
- `unnecessary_commit_delta`: 2
- `detection_latency_seconds`: 48
- `fix_duration_seconds`: 241
- Friction-Klasse: semantic_friction (Hauptfehler), structural_friction (zusätzlicher canonical-contract Drift bei Konsolidierung)
- Was schief lief: kontrolliert injizierter Schema-Verstoß (fehlender required key `context` in einer Evidence-Zeile)
- Schritte zur Behebung: 2 (schema-fix commit; danach system-map-Regeneration für canonical contract)

**Run-006 / PR-67** (natürliche clean_reference ohne Injektion):
- `ci_blocking_failures_total`: 1
- `manual_regen_steps`: 1
- `diagnosis_clarity_score`: 5/5
- `unnecessary_commit_delta`: 1
- `detection_latency_seconds`: 97
- `fix_duration_seconds`: 36
- Friction-Klasse: structural_friction
- Was passierte: minimaler canonical Change in `docs/foundations/vision.md`; zwei Generate-Läufe ohne zusätzlichen Diff. Im PR schlug `validate` einmal am canonical-contract (`system-map.md` stale) fehl und wurde durch `make generate-canonical` behoben.

### Diagnosis Clarity
Run-001: nicht gemessen. Run-003: 5/5 (sauber, keine Unklarheit über Fehlerursachen). Run-004: 4/5 (schnell lokalisierbarer Schema-Fehler mit präziser Fehlstelle). Run-005: 5/5 (lokaler, eindeutig klassifizierter Fehler mit direkter Behebung). Run-006: 5/5 (struktureller Fehler im Validate-Log direkt mit konkreter Diff-Ursache ausgewiesen).

## Deutung

> Interpretation, explizit als solche markiert.

Der Kontrast zwischen Run-001 (mehrere Regenerationszyklen), Run-002 (ein blockierender CI-Fehler mit Fix-Zyklus) und Run-003 (initial sauberer Lauf) deutet auf sinkende Friction hin. Das bleibt Interpretation, weil Ursachenmix und Messdisziplin über die Runs noch nicht vollständig vereinheitlicht sind.

## Verdict

Vorläufig offen. Sechs dokumentierte PR-Runs liegen vor. Run-006 lieferte einen natürlichen Vergleichspunkt, erfüllte aber die clean_reference-Kriterien nicht, weil strukturelle Konsolidierungsfriktion weiterhin auftrat.

## Lessons Learned

- Canonical artifacts erwiesen sich in Run-001 als anfällig: generator-bugs lösten mehrfache Regenerationszyklen aus.
- Run-002 zeigte, dass CI-Fehler/Fix-Zyklen metrikfähig dokumentierbar sind.
- Run-003 war der erste initial saubere End-to-End-Lauf mit vollständiger Metrikerhebung.
- Die Determinismus-Prüfung (double-run check) ist reproduzierbar und schnell.
- Run-005 bestätigt, dass kontrollierte semantische Friktion reproduzierbar injizierbar und mit stabilen Zeitmetriken messbar ist.
- Run-006 zeigt, dass strukturelle Konsolidierungsfriktion auch ohne künstliche semantische Injektion auftreten kann.

## Nächste Schritte

- Cross-Run-Entscheidungsoberfläche in `results/cross-run-assessment.md` pflegen und als Pflichtreferenz vor jedem Switch auf `result_assessment` verwenden.
- Messdefinitionen über Run-001/Run-002/Run-003 harmonisieren (gleiches Feldset, gleiche Scope-Interpretation).
- Für einen Wechsel auf `result_assessment` einen weiteren natürlichen Lauf ohne Konsolidierungsfix anstreben oder das strukturelle Pattern als erwartetes Workflow-Verhalten explizit isolieren.
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
