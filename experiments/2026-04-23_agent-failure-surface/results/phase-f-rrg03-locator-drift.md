---
title: "Phase F — RRG-03 Locator Drift After Partial Apply (Diagnosis-First)"
status: draft
canonicality: operative
created: "2026-04-30"
updated: "2026-04-30"
author: "Claude Opus 4.7"
relations:
  - type: references
    target: ../method.md
  - type: references
    target: result.md
  - type: references
    target: replay-gap-candidates.md
  - type: references
    target: evidence.jsonl
  - type: references
    target: ../artifacts/run-phase-f-rrg03/run_meta.json
  - type: references
    target: ../artifacts/run-phase-f-rrg03/execution.txt
---

# Phase F — RRG-03 Locator Drift After Partial Apply (Diagnosis-First)

## These / Antithese / Synthese

- **These:**
  Der aktuelle Dry-Run kann Locator-Drift nach partieller Mutation nicht
  beweisen, weil er keine reale Datei-I/O und keine Re-Resolution gegen den
  mutierten Dateistand ausführt.
- **Antithese:**
  Wenn Locator rein deklarativ bleibt, ist Drift außerhalb des
  Replay-Scopes und darf nicht als Runner-Fehler klassifiziert werden.
- **Synthese:**
  Phase F prüft RRG-03 zunächst über ein kontrolliertes Minimal-Szenario,
  ohne den Runner zu ändern.

## Ziel

Phase F / RRG-03 *vorbereiten*, nicht lösen. Konkret: eine reproduzierbare
Versuchsanordnung für den Kandidaten **RRG-03 — Locator-Drift-After-Partial-Apply**
(siehe `results/replay-gap-candidates.md`) als kommitierte Fixtures festschreiben
und das diagnostische Vokabular (`stable`, `drifted`, `ambiguous`, `not_found`)
sowie ein präzises Patch-Gate definieren — bevor irgendetwas am Runner, am
Schema oder an Validatoren angefasst wird.

## Scope

- Additive Dokumentations- und Fixture-Artefakte unter
  `experiments/2026-04-23_agent-failure-surface/artifacts/run-phase-f-rrg03/`.
- Einmalige zusätzliche Evidenzzeile am Ende von
  `experiments/2026-04-23_agent-failure-surface/results/evidence.jsonl`.
- Ein minimaler Verweis aus
  `experiments/2026-04-23_agent-failure-surface/results/result.md` auf dieses
  Dokument.
- Ggf. additiver `execution_ref` im Manifest.

## Nicht-Ziele

- **Keine Änderung** an `tools/vibe-cli/replay_minimal.py`.
- **Keine Änderung** an `schemas/replay.trace.schema.json`.
- **Keine Änderung** an `scripts/docmeta/validate_command_chain.py`.
- **Keine Änderung** an Validatoren oder Tests.
- **Keine Änderung** an `.github/workflows/validate.yml`.
- **Kein neuer CI-Gate.**
- **Keine** Behauptung, RRG-03 sei bewiesen.
- **Kein** `passed_but_wrong`-Urteil, solange kein realer Mutationsbeleg
  existiert.
- **Keine** Phase-5-Nacharbeit (Phase 5 ist als `out_of_scope_documented`
  abgeschlossen; siehe `result.md` und `phase5-adversarial-agent-simulation.md`).

## Diagnose-Baseline

Belegter Ist-Zustand aus Phase 4 (siehe `replay-gap-candidates.md`):

1. `replay_minimal.py` ist explizit non-mutativ:
   `step["would_mutate"] = False`,
   `"mode": "dry_run"`,
   `"non_mutation_guarantee": True`.
2. Das v0.2-Replay-Schema *erzwingt* Dry-Run-Semantik:
   `"mode": { "const": "dry_run" }`,
   `"would_mutate": { "const": false }`,
   `"summary.non_mutation_guarantee": { "const": true }`.
3. `locator` wird im Replay-Step nur übernommen / redacted, **nicht** gegen
   einen realen Dateistand aufgelöst.
4. Bestehende Replay-Tests prüfen Determinismus, Schema-Konformität und
   Nicht-Mutation, aber **keine** reale Re-Resolution nach partieller
   Mutation.

Daraus folgt für Phase F: Ohne reale Datei-I/O und ohne Re-Resolution gegen
einen mutierten Dateistand kann RRG-03 *nicht* bewiesen werden — und
darf entsprechend hier nicht als bewiesen markiert werden.

## Hypothesen (max. 3)

- **H-F1:** Wenn Step A eine Datei real partiell mutiert und Step B
  anschließend einen Locator gegen den mutierten Stand auflöst, kann der
  Locator auf eine andere Stelle zeigen als die C1-Baseline-Resolution vor Step A.
- **H-F2:** Bei semantisch ähnlichen, mehrfach vorhandenen Locator-Strings
  (z. B. `"Validate token"` in zwei benachbarten Abschnitten) ist die
  Auflösung nach partieller Mutation **mehrdeutig** (`ambiguous`), nicht nur
  verschoben.
- **H-F3:** Ein Locator kann durch Step A *unauffindbar* werden
  (`not_found`), wenn der Anker-Kontext entfernt oder umstrukturiert wurde.

## Minimaler Beweisplan (2–5 Checks)

Diese Checks sind hier nur **deklariert**, nicht ausgeführt. Eine
Ausführung erfordert reale Datei-I/O und ist explizit *nicht* Teil
dieses PRs.

1. **C1 — Baseline-Resolution (vor Step A):**
   Locator aus `step-b.json` gegen `fixtures/before.md` auflösen und die
   getroffene Stelle (Zeile, Byte-Range, Match-Index) festhalten.
2. **C2 — Reale Anwendung Step A:**
   Step A in einem isolierten Temp-Workspace tatsächlich anwenden, sodass
   `before.md` nachweisbar verändert wird (Hash-Vergleich vor / nach).
3. **C3 — Re-Resolution nach Step A:**
   Locator aus `step-b.json` erneut gegen den **mutierten** Dateistand
   auflösen und das Ergebnis mit C1 vergleichen.
4. **C4 — Klassifikation:**
   Das Delta aus C1 → C3 in genau eine der vier Klassen einordnen:
   `stable`, `drifted`, `ambiguous`, `not_found`.
5. **C5 — Dry-Run-Baseline-Abgleich:**
   Den aktuellen Dry-Run-Trace für Step B (ohne Step-A-Anwendung) erzeugen
   und festhalten, dass der Dry-Run non-mutativ ist und keine Post-Apply-
   Re-Resolution ausführt — er ist eine non-mutating baseline, kein Orakel,
   das `stable` für den Post-Apply-Zustand behauptet. Damit kann der
   Dry-Run die Klassen `drifted`, `ambiguous` oder `not_found` weder
   bestätigen noch ausschließen.

## Stop-Kriterium

Phase F / RRG-03 wird als *vorbereitet* abgeschlossen, sobald die
Fixture-Struktur und das diagnostische Vokabular kommittet sind und
`make validate` grün bleibt — **ohne** dass damit ein Beweis für oder
gegen RRG-03 behauptet wird. Eine inhaltliche Phase-F-Aussage entsteht
erst nach realer Ausführung des Beweisplans (C1–C5).

## Erwartete Klassifikationen

| Klasse | Bedeutung |
| ------ | --------- |
| `stable` | Locator aus Step B trifft nach Step A dieselbe Stelle wie die C1-Baseline-Resolution vor Step A. |
| `drifted` | Locator trifft nach Step A eine andere Stelle als die C1-Baseline-Resolution vor Step A (verschobene Anker / shifted offsets). |
| `ambiguous` | Locator passt nach Step A auf mehrere Stellen, ohne deterministischen Tie-Breaker. |
| `not_found` | Locator passt nach Step A auf keine Stelle mehr. |

Aktueller Diagnosezustand: `not_proven` (siehe
`fixtures/expected.json#diagnosis_class`).

## Patch-Gate

**Patch nur dann**, wenn ein kontrollierter Fixture-Run zeigt, dass ein
Folgekommando nach **realer** Mutation anders adressiert als in der
Baseline — d. h. die beobachtete Klasse ist `drifted`, `ambiguous`
oder `not_found`, während der Dry-Run als non-mutating baseline keine
Post-Apply-Re-Resolution durchführt und diese Klassen nicht modellieren kann.

Solange dieser Beleg nicht existiert:

- `RRG-03 proof status: NOT_PROVEN`
- `Patch-Gate: NOT_TRIGGERED`

## Risikoanalyse

- **Niedriges Risiko:** Es wird keine Runtime-Logik geändert. Der
  bestehende Dry-Run-Vertrag, die Schemas und die Validatoren bleiben
  unangetastet. `make validate` bleibt grün.
- **Mittleres Risiko (Sprache):** Das Hauptrisiko ist sprachlicher
  Natur — Planungsdokumente können den Eindruck erwecken, RRG-03 sei
  bereits belegt. Gegenmaßnahmen:
  - explizites `proof status: NOT_PROVEN`,
  - explizites `Patch-Gate: NOT_TRIGGERED`,
  - `diagnosis_class: not_proven` in `fixtures/expected.json`,
  - `provenance_intent: planned_fixture` in `run_meta.json`,
  - `execution.txt` ist als Planungs-/Vorbereitungslog markiert und
    enthält keine erfundenen CLI-Outputs.
- **Sekundärrisiko (Scope-Creep):** Die Versuchung, „nebenbei" einen
  Locator-Resolver oder ein neues Schema-Feld einzuführen, wird durch
  die explizite Liste der Nicht-Ziele und durch das harte Patch-Gate
  begrenzt.

## Alternativpfad

Falls ein realer Phase-F-Lauf RRG-03 belegt, ist der **bevorzugte**
strukturelle Pfad **nicht**, die Locator-Resolution im Runner zu härten.
Stattdessen:

> Command-Contracts später so erweitern, dass Folgekommandos explizite
> *post-apply anchors* oder *byte ranges* referenzieren, statt einen
> opaken Locator-String erneut gegen den mutierten Dateistand
> aufzulösen.

Damit bleibt die Verantwortung dort, wo sie entstanden ist
(Command-Vertrag), statt einen weiteren Runtime-Locator-Resolver an
den Replay-Pfad zu kleben.

## Lieferumfang dieses PRs (Diagnosis-First)

- Diese Datei: `results/phase-f-rrg03-locator-drift.md`.
- Artefaktordner:
  `artifacts/run-phase-f-rrg03/` mit
  `fixtures/before.md`, `fixtures/step-a.json`, `fixtures/step-b.json`,
  `fixtures/expected.json`, `run_meta.json`, `execution.txt`.
- Eine zusätzliche Evidenzzeile am Ende von
  `results/evidence.jsonl`
  (`metric: phase_f_rrg03_planning_started`).
- Minimaler Verweis aus `results/result.md`.
- Additiver `execution_ref` im `manifest.yml`.

Klare Aussage:

- **RRG-03 proof status: NOT_PROVEN**
- **Patch-Gate: NOT_TRIGGERED**
