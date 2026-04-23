---
title: "Methode: Agent Failure Surface Mapping"
status: draft
canonicality: operative
created: "2026-04-23"
updated: "2026-04-23"
author: "Claude Opus 4.7"
---

# method.md — Methode

## Hypothese (Gesamt)

Die Grenze zwischen „agentisch korrekt" und „agentisch falsch" ist im
aktuellen Contract-/Fixture-Layer **nicht überall scharf**. Gezielt
konstruierte Drift-, Widerspruchs-, Chain- und Replay-Fälle decken
Toleranzzonen auf, die sich in Fixtures, Tests oder Validator-Änderungen
überführen lassen.

Die Reihe prüft diese Gesamthypothese über fünf Phasen mit eigenen,
falsifizierbaren Teilhypothesen.

## Gesamtvorgehen

Pro Phase gilt dieselbe Disziplin (angelehnt an den ursprünglich verworfenen
Hardening-Task, aber evidenzbasiert statt blind):

1. **Diagnose (repo-abgeleitet):** Ist-Zustand messen, nicht vermuten.
2. **Injection:** konstruierter Stör-/Drift-/Widerspruchsfall.
3. **Beobachtung:** wird die Injektion erkannt? wo genau nicht?
4. **Strukturkonsequenz:** Fixture, Test oder Validator-Änderung.
5. **Re-Validierung:** `make validate` vor und nach der Konsequenz, mit
   dokumentiertem Signalwechsel.

Jede Phase ist in einem **eigenen nachgelagerten PR** auszuführen. Dieser
PR hier ist der Design-Rahmen.

## Patch-Gate

Eine Strukturkonsequenz (Fixture/Test/Validator) darf nur eingebaut werden,
wenn für sie mindestens **ein** konkreter Beleg existiert:

- ein Repo-Snippet, das die Toleranz zeigt, ODER
- ein fehlschlagendes Szenario mit `evidence.jsonl`-Eintrag, ODER
- ein Validator-Output, der die fehlende Erkennung belegt.

Spekulatives Patchen ist untersagt. Siehe `AGENTS.md` §„Verhaltensregeln"
Punkt 2 („Keine Eigeninterpretation") und `agent-policy.yaml`.

## Metriken

Für jede Phase werden mindestens erhoben:

- **Toleranz-Rate:** Anteil injizierter Drift-/Widerspruchsfälle, die vom
  bestehenden Validator-Set **nicht** erkannt wurden.
- **Konsequenz-Abdeckung:** Anteil identifizierter Toleranzzonen, die in
  derselben PR-Serie in Fixture/Test/Validator überführt wurden.
- **Regressionssignal:** ob `make validate` vor der Konsequenz die Injektion
  akzeptierte und nach der Konsequenz ablehnte.

Die Metriken werden in `evidence.jsonl` pro Run als `measurement`-Records
festgehalten.

## Erfolgskriterien (Gesamtreihe)

Die Reihe gilt als erfolgreich, wenn nach Abschluss aller fünf Phasen gilt:

- mindestens eine bislang tolerierte Fehlklasse je Phase ist als Fixture +
  Test verankert, **oder**
- die Phase hat explizit und begründet ergeben, dass keine neue Toleranz
  gefunden wurde (negative Evidenz ist ebenfalls gültig; dann Eintrag in
  `failure_modes.md`).

Scheintreffer („formal gefunden, aber nicht testbar gemacht") zählen nicht.

---

## Phase 1 — Drift Injection

### Teil-Hypothese

Validatoren erkennen **harte** Strukturverletzungen, aber tolerieren
**kleine Drifts** (Off-by-one im Locator, leicht verändertes `target_files`,
marginale Hash-Unterschiede).

### Antithese

Hash- und Schema-Checks sind ausreichend scharf; kleine Drifts werden
erkannt, weil die Fehlerklasse unterhalb der Schwelle nicht existiert.

### Diagnose (vor Injektion)

- `tests/fixtures/agent_handoff/hash-mismatch.json` existiert (prüft harten
  Mismatch).
- `tests/fixtures/command_chains/invalid-empty-locator.json` existiert (prüft
  leeren Locator).
- `tests/fixtures/command_chains/invalid-target-files-mismatch.json` existiert
  (prüft Target-Mismatch).

**Offen:** Verhalten bei **marginaler** Abweichung (ein Zeichen, ein Pfad
mit Trailing-Slash, Hash mit einem Bit-Flip an hoher Stelle).

### Injektions-Set (mindestens 6 Fälle)

Jeder Fall wird aus einer bekannten `valid-*`-Fixture abgeleitet:

1. Locator: Offset ±1 Zeile.
2. Locator: Anchor mit zusätzlichem Leerzeichen.
3. `target_files`: Pfad mit Trailing-Slash.
4. `target_files`: relativer vs. normalisierter Pfad (`./docs/x.md` vs.
   `docs/x.md`).
5. Handoff-Hash: ein Zeichen geändert an einer hohen Stelle (erkannt?).
6. Handoff-Hash: gekürzt auf 63 Zeichen (sichtbar ungültig?).
7. optional: Unicode-Homoglyph (z.B. kyrillisches `а` in einem Pfad).

### Erfolgssignal

Mindestens **einer** der Fälle wird vom aktuellen Validator-Set akzeptiert,
obwohl er fachlich falsch ist. → Fixture (`contract_invalid` oder neue
Drift-Klasse) + Validator-Test folgen im selben PR.

### Stop-Bedingung Phase 1

Entweder mindestens ein unerkannter Drift ist testbar verankert, oder
sämtliche Fälle werden erkannt; im zweiten Fall: `failure_modes.md`-Eintrag
mit Belegen.

---

## Phase 2 — Semantic Contradiction

### Teil-Hypothese

Semantische Widersprüche zwischen Command und Handoff (formal gültig, logisch
inkonsistent) werden schwerer erkannt als syntaktische Verletzungen.

### Antithese

Cross-Contract-Validatoren decken Semantik implizit über `target_drift`,
`state_drift` und `semantic_contradiction` bereits ab.

### Diagnose (vor Injektion)

Vorhandene Cross-Contract-Fixtures (siehe
`tests/fixtures/cross_contract/invalid/`):

- `contradiction.json` — `semantic_contradiction`
- `target_drift.json`, `target_drift_extra.json` — `handoff_target_drift`
- `state_drift.json` — `handoff_state_drift`
- `semantic_mismatch.json` — `handoff_intent_mismatch` + `validate_without_write`

**Offen:** formal gültige Sequenzen, bei denen Command und Handoff sich
inhaltlich widersprechen, ohne dass eines der vorhandenen Fehlerlabels greift.

### Injektions-Set (mindestens 6 Fälle)

1. `write_change` mit `locator` in Datei X, Handoff `target_files: [Y]` —
   formgerecht, aber leerer Schnitt.
2. `write_change: add` mit `exact_after` leer, aber Handoff beschreibt
   „content added".
3. Command-Kette modifiziert Datei, Handoff behauptet `unchanged`.
4. `validate_change: success: true` bei Chain mit `write_change`, der auf
   Datei zielt, die der Handoff nicht als `touched` führt.
5. `read_context` behauptet Fakt über Datei, die nicht in `target_files` steht.
6. Reihenfolge-Widerspruch: Handoff impliziert Schritt A vor B, Chain zeigt
   B vor A.

### Erfolgssignal

Mindestens einer dieser Fälle passiert alle bestehenden Validatoren, obwohl
er logisch inkonsistent ist. → Cross-Contract-Fixture + Test.

### Stop-Bedingung Phase 2

Wie Phase 1.

---

## Phase 3 — Chain Integrity Stress

### Teil-Hypothese

Fehler entstehen in **Transitions** (Mitte der Chain), nicht in
Einzel-Commands. Chain-Validatoren prüfen Einzelschritte strenger als
Übergänge.

### Antithese

Die Chain-Validatoren decken Transitions über `command_sequence_invalid`,
`locator_continuity_violation` und `validate_without_write` bereits vollständig ab.

### Diagnose (vor Injektion)

Vorhandene Chain-Fixtures in `tests/fixtures/command_chains/` (15 Dateien).
Fokus: **`valid → valid → invalid → valid`**-Muster — sind diese in der
aktuellen Suite repräsentiert?

### Injektions-Set (mindestens 6 Fälle)

1. Chain mit drei gültigen Schritten und einem dazwischenliegenden Schritt,
   dessen `locator` inkonsistent zum Vorgänger ist.
2. Chain `write → write → validate` ohne zwischenzeitliches `read_context`
   (bewusst, prüfen ob Warnklasse existiert oder fehlt).
3. Chain mit gültigen Einzelcommands, aber zusammengenommen widersprüchliche
   `change_type`-Abfolge (`add` dann `remove` auf derselben Stelle).
4. Chain, die mitten in der Sequenz die `version` wechselt (v0.1 → v0.2).
5. Chain mit leerer Zwischen-Sequenz (nur `read_context` und `validate_change`
   ohne `write_change`).
6. Chain, die `validate_change.errors` enthält, aber danach weiter fortfährt
   (kein Abbruch).

### Erfolgssignal

Mindestens eine Transition wird nicht als invalid erkannt.

### Stop-Bedingung Phase 3

Wie Phase 1.

---

## Phase 4 — Replay Reality Gap

### Teil-Hypothese

Der Dry-Run-Replay modelliert nicht alle Effekte einer hypothetischen
Realausführung. Es gibt Kandidatenklassen, die im Dry-Run nicht sichtbar wären.

### Antithese

Der Dry-Run ist per Design non-mutativ und repräsentiert den
Validierungs-Happy-Path korrekt; reale Ausführung ändert nichts an der
Validierungssemantik.

### Methodischer Hinweis

Diese Phase ist **qualitativ**. Ohne echten Runner (Phase F) kann nur
argumentativ Evidenz erhoben werden. Das Ergebnis ist eine
**Kandidatenliste** für Phase F, keine quantitative Messung. Das ist
explizit als Einschränkung in `failure_modes.md` zu dokumentieren.

### Untersuchungsfragen

1. Welche Zustandsänderungen (Disk, Git-Index, Locator-Drift durch voran­
   gehende Änderungen) sind im Dry-Run nicht modellierbar?
2. Welche Fehlerklassen setzen eine **Reihenfolge tatsächlicher** Änderungen
   voraus (z.B. Locator in Schritt 3 ist nur gültig, wenn Schritt 2
   angewendet wurde)?
3. Welche Validierungen sind idempotent und welche nicht?

### Output

- Liste „Replay-Lügen" in `results/replay-gap-candidates.md` (PR-spezifisch).
- Einträge werden als `observation`-Records in `evidence.jsonl` erfasst.
- Kandidatenliste wird **nicht** als neue Fixture-Klasse eingebaut, solange
  kein echter Runner existiert. Stattdessen: Referenzeintrag in der
  Fixture-Matrix unter „Intentional Gap — Replay".

### Stop-Bedingung Phase 4

Mindestens drei Kandidaten identifiziert + in Matrix verlinkt, oder
begründete Negativ-Aussage.

---

## Phase 5 — Adversarial Agent Simulation

### Teil-Hypothese

Ein Agent, der bewusst „minimal gültig, maximal falsch" arbeitet, kann den
bestehenden Validator- und Fixture-Layer täuschen — nicht durch harte
Fehler, sondern durch die Kombination formal gültiger, semantisch leerer
Outputs.

### Antithese

Die Kombination aus Schema-, Chain- und Cross-Contract-Validierung verhindert
auch solche „Form-ohne-Gehalt"-Outputs systematisch.

### Injektions-Set (mindestens 4 Simulationen)

1. Agent erzeugt `read_context` mit `extracted_facts: ["ok"]` — formal gültig,
   inhaltlich leer.
2. Agent erzeugt `write_change` mit trivialer Modifikation (z.B. Whitespace),
   Handoff behauptet inhaltliche Änderung.
3. Agent erzeugt `validate_change: success: true` ohne Bezug zur tatsächlichen
   Änderung.
4. Agent erzeugt vollständige Chain, die **alle Pflichtfelder** erfüllt, aber
   keine operative Wirkung hätte (Null-Change).

### Erfolgssignal

Mindestens eine Simulation passiert den gesamten Validatoren-Stack, obwohl
sie epistemisch wertlos ist. → Entweder neuer Constraint (z.B.
`non-empty-change`-Guard) oder explizite Dokumentation als „außerhalb der
Validator-Zuständigkeit".

### Stop-Bedingung Phase 5

Wie Phase 1, mit der Zusatzregel: Entscheidungen über „außerhalb der
Validator-Zuständigkeit" sind in `decisions/process/` zu dokumentieren, nicht
nur in `failure_modes.md`.

---

## Coverage-Output (verpflichtend pro Phase-PR)

Jeder Phase-PR muss ergänzen:

- Abdeckte Äquivalenzklassen (Tabelle in PR-Beschreibung).
- Bewusst nicht abgedeckte Klassen (mit Begründung).
- Aktualisierung der Fixture-Matrix (`docs/reference/agent-operability-fixture-matrix.md`).

## Dokumentationsregel

Dokumentation spiegelt tatsächliches Verhalten, nicht Absicht. Wenn eine
Phase zeigt, dass ein Constraint nicht greift: Entweder Constraint härten
oder Matrix-Eintrag auf `covered: false` setzen. Nicht still dulden.

## Forbidden (für alle Phasen)

- Keine neuen Architekturschichten.
- Keine semantische Systemerweiterung über Phase-E hinaus.
- Keine Abstraktion ohne verankerten Testbeleg.
- Keine stille Statusaufwertung (`AGENTS.md` §„Verbot unbelegter
  Status-Umdeutung").

## Prinzip

> Wenn ein Verhalten nicht testbar ist, existiert es nicht.
> Wenn ein Constraint nicht durchgesetzt ist, existiert er nicht.

Diese Reihe macht Fehler **sichtbar und billig** — sie ist kein
Präventionsversuch, sondern Detektions-Härtung.
