---
title: "Cross-Run-Auswertung: Generated Artifact Contract Validation"
status: draft
canonicality: operative
relations:
  - type: informed_by
    target: result.md
---

# Cross-Run-Auswertung — Generated Artifact Contract Validation

## 1. Bewertungsrahmen

### Zielhypothese
Die Trennung in `canonical` / `derived` / `ephemeral` plus das CI-Splitting in `blocking` / `non-blocking` / `artifact-only` reduziert operative Friktion oder macht sie klarer, lokalisierbarer und billiger zu beheben.

### Bewertungsmodus
Diese Auswertung dient als Grundlage fuer einen moeglichen Wechsel von `decision_type: execution_assessment` zu `decision_type: result_assessment`.

## 2. Baseline Definition

Baseline dient als Referenzpunkt fuer Friktionsbewertung.

Aktueller Vorschlag:
- Primaere Baseline: Run-001 (real, hohe Friktion, geringe Metrikdisziplin)
- Sekundaere Referenz: Run-002 (erste instrumentierte Form)

Nicht-Baseline:
- Run-004, Run-005 (kontrollierte Friktion)
- Run-003 (Optimalszenario, aber kein Gegenpol)

Zweck:
- Trennung von natuerlicher Friktion
- kontrollierter Friktion
- idealem Ablauf

Einschraenkung:
- Es gibt aktuell keine saubere no-contract Baseline; die Baseline bleibt deshalb eine explizite Vergleichsrahmung und kein Gegenbeweis ohne Contract-Split.

## 3. Run-Matrix

| Run | PR | Typ | Scope-Klasse | evaluation_role | Friction-Profil | Harmonisiert | Bewertbar fuer Hypothese |
|---|---|---|---|---|---|---|
| Run-001 | PR-58 | real | frueh / heterogen | historical_baseline | hohe reale In-PR-Friktion | teilweise | eingeschraenkt |
| Run-002 | PR-61 | real | klein, instrumentiert | transitional | blocking failure + fix cycle | besser | ja, eingeschraenkt |
| Run-003 | PR-62 | real | klein, sauber | clean_reference | clean run | gut | ja |
| Run-004 | PR-63 | kontrolliert | klein, kontrollierte Friktion | controlled_probe | semantic + structural | gut | bedingt |
| Run-005 | PR-64 | kontrolliert | klein, kalibriert | calibration | semantic + structural | gut | bedingt |

### Rollen-Semantik
- `historical_baseline`: frueher Realzustand mit hoher Friktion und unvollstaendiger Metrikdisziplin
- `transitional`: erste instrumentierte Zwischenform mit begrenzter Vergleichbarkeit
- `clean_reference`: sauberer Referenzlauf ohne initiale blocking failures
- `controlled_probe`: gezielt gestoerter Lauf zur Beobachtung kontrollierter Friktion
- `calibration`: Wiederholung eines kontrollierten Musters zur Stabilisierung der Vergleichbarkeit

## 4. Kernmetriken (normalisierte Sicht)

### 3.1 Erfasste Metriken
- `ci_blocking_failures_total`
- `manual_regen_steps`
- `diagnosis_clarity_score`
- `unnecessary_commit_delta`
- `detection_latency_seconds`
- `fix_duration_seconds`

### 3.2 Friction-Klassen
- `semantic_friction`
- `structural_friction`

## 5. Structural Friction Pattern

Beobachtung:
- Wiederholter CI-Fehler: stale `system-map.md` bei Artefakt-Konsolidierung

Eigenschaften:
- tritt nach Artifact-Adds auf
- unabhaengig von `semantic_friction`
- deterministisch reproduzierbar

Offene Frage:
- Workflow-Artefakt (expected)
- oder Architekturproblem (unexpected)

Status:
- Noch nicht isoliert; verhindert derzeit eine klare Hypothesenbewertung.

## 6. Beobachtungen (nur belegt)

### Run-001
- Mehrfache canonical-Regenerationszyklen innerhalb eines PRs.
- Path-resolution bug und .venv leak beobachtet.
- Hohe reale Friktion bei unvollstaendiger Metrikdisziplin.

### Run-002
- Unabhaengiger PR-Run mit einem blocking failure und Fix-Zyklus.
- Metrikdisziplin besser als Run-001, aber noch Uebergangscharakter.

### Run-003
- Erster sauberer End-to-End-Lauf.
- 0 initiale blocking failures.
- Determinism check bestanden.

### Run-004
- Kontrollierte semantic_friction injiziert.
- Blocking failure absichtlich erzeugt und schnell lokalisiert.
- Zusaetzlicher structural failure bei Konsolidierung (stale system-map).

### Run-005
- Kontrollierte semantic_friction erneut injiziert.
- Reproduzierbare Messung mit konsistenten Zeitmetriken.
- Structural consolidation failure erneut beobachtet.

## 7. Kontrastive Deutung

### Deutung A (optimistisch)
Die Architektur entmischt Friktion:
- semantic failures werden schnell lokalisierbar,
- structural failures werden als eigener Typ sichtbar,
- clean runs bleiben moeglich,
- kontrollierte Friktion ist reproduzierbar messbar.

### Deutung B (skeptisch)
Die Architektur koennte Friktion eher umlagern als reduzieren:
- ein Teil der Kosten verschiebt sich in formale Fehlerklassen,
- Konsolidierungsfehler (`stale system-map`) treten wiederholt auf,
- der staerkste Vorteil liegt eventuell in Diagnoseklarheit statt Friktionssenkung.

## 8. Zwischenfazit

### Belastbar sagbar
- Friktion ist klarer klassifizierbar als vor dem Contract-Split.
- Clean runs sind moeglich.
- Semantic friction ist schnell detektierbar und behebbar.
- Structural friction bei Konsolidierung zeigt ein wiederkehrendes Muster.
- Kontrollierte Friktion ist reproduzierbar messbar.

### Noch nicht belastbar sagbar
- Dass das Modell Friktion insgesamt reduziert.
- Dass das CI-System insgesamt effizienter ist.
- Dass die Architektur bereits adoptable ist.
- Dass der beobachtete Vorteil generalisiert.

## 9. Decision Trigger

Switch to `result_assessment` wenn:

1. mindestens 2 `clean_reference` Runs existieren
2. `structural_friction` isoliert oder stabil erklaert ist
3. die Baseline explizit definiert und akzeptiert ist
4. alle 6 Kernmetriken vollstaendig vergleichbar sind

## 10. Candidate Verdict Mapping

### `confirms`
Nur wenn belegt ist:
- clean runs sind keine Ausnahme,
- Friktion wird im Mittel geringer oder billiger,
- structural failure pattern ist verstanden oder behoben.

### `mixed`
Wenn belegt ist:
- Diagnoseklarheit steigt,
- Friktion sinkt aber nicht klar,
- oder Friktionstypen eher getrennt als reduziert werden.

### `inconclusive`
Wenn belegt ist:
- Runs existieren,
- aber Scope und Vergleichslogik noch nicht stabil genug sind.

### `refutes`
Nur wenn belegt ist:
- Contract-Split erzeugt systematisch neue oder teurere Friktion,
- clean runs bleiben Ausnahme,
- Wiederholung verbessert nichts.

## 11. Aktueller methodischer Default

Empfohlener Zielkorridor fuer einen spaeteren `result_assessment`: `mixed` oder `inconclusive`.
Noch nicht freigeben, bis Vergleichsnormalisierung explizit abgeschlossen ist.

## 12. Offene Leerstelle

Es fehlt:
- eine explizite Baseline-Definition ohne Contract,
- eine bereinigte Vergleichsmatrix ohne Altlastverzerrung,
- eine belastbare Entscheidung, ob `stale system-map` primaer Workflow-Artefakt oder Architekturfehler ist.
