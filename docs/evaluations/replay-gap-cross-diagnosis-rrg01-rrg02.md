---
title: "Cross-Diagnosis RRG-01 / RRG-02 gegen RRG-03-Remediation-Kandidaten"
status: draft
canonicality: operative
created: "2026-04-30"
updated: "2026-04-30"
author: "Copilot Agent"
relations:
  - type: references
    target: "rrg03-remediation-strategy-comparison.md"
  - type: references
    target: "../../experiments/2026-04-23_agent-failure-surface/results/replay-gap-candidates.md"
  - type: references
    target: "../../experiments/2026-04-23_agent-failure-surface/results/phase-f-rrg03-locator-drift.md"
  - type: references
    target: "../../experiments/2026-04-23_agent-failure-surface/results/evidence.jsonl"
  - type: references
    target: "../../decisions/process/2026-04-30-rrg03-remediation-boundary.yml"
  - type: references
    target: "../../contracts/command-semantics.md"
---

# Cross-Diagnosis RRG-01 / RRG-02 gegen RRG-03-Remediation-Kandidaten

## These / Antithese / Synthese

**These:** RRG-03 ist durch zwei Real-Runs fixture-spezifisch belegt.
Die Remediation-Kandidaten sind für RRG-03 bewertet.
Dasselbe Kandidatenset sollte auch für RRG-01 und RRG-02 gelten.

**Antithese:** RRG-01 und RRG-02 sind bisher nur als qualitative Inventur
(Phase 4) dokumentiert — kein realer Ausführungsbeleg.
Die Übertragung von RRG-03-Befunden auf RRG-01/RRG-02 ohne eigene Beweise
wäre epistemischer Größenwahn.

**Synthese:** Diese Diagnose prüft, ob RRG-01 und RRG-02 dieselbe Remediation-Klasse
wie RRG-03 teilen oder eigene Drift-Ursachen besitzen — ohne Patch, ohne Decision
Preimage, ohne Status-Aufwertung. Ziel ist ein belegter Diagnosebefund, der als
Grundlage für spätere Real-Runs und eventuelle Entscheidungen dienen kann.

---

## Belegter Ist-Zustand

### RRG-03 Real-Runs (belegt)

Quelle:
`experiments/2026-04-23_agent-failure-surface/results/phase-f-rrg03-locator-drift.md`

| | Run 01 (removal-drift) | Run 02 (injection-before-drift) |
|---|---|---|
| Fixture | Auth Flow Notes, Locator `"Validate token"` | API Gateway Notes, Locator `"Process request"` |
| Drift-Muster | Erster Treffer entfernt → nächster Treffer rückt auf Index 0 | Neuer Treffer oberhalb eingefügt → Index 0 zeigt auf Injektion |
| C1 match_count / line | 2 Treffer / Zeile 4 | 3 Treffer / Zeile 7 |
| C3 match_count / line | 1 Treffer / Zeile 7 | 4 Treffer / Zeile 4 |
| Klassifikation | drifted | drifted |
| patch_gate.triggered | true | true |
| proof_scope | fixture_only | fixture_only |

**Belegt:** Locator-Drift tritt auf, wenn ein text-basierter Locator in einem
Folge-Schritt nach einer realen Mutation ohne erneute Auflösung genutzt wird.
Der Drift basiert auf der Schwäche, dass `locator` nur ein menschlich lesbarer
Anker ist — keine stabile Identität.

---

### RRG-01: Disk-State-Apply-Delta (nicht real-run-belegt)

Quelle:
`experiments/2026-04-23_agent-failure-surface/results/replay-gap-candidates.md`
Spalte: `RRG-01 Disk-State-Apply-Delta`

| Feld | Wert |
|------|------|
| Betroffene Achse | Disk-State, Idempotenz vs. Nicht-Idempotenz, Validierung nach Mutation |
| Status in replay-gap-candidates.md | `candidate_for_phase_f` |
| Priorität | Phase F: nach RRG-03 |
| Real-Run-Beleg | **nicht vorhanden** |

**Beschreibung (aus replay-gap-candidates.md):**
Reale `write_change`-Anwendung kann Disk-Inhalt verändern (z.B. line endings,
normalization, conflict markers). Der Dry-Run meldet weiter `would_mutate: false`.
Es gibt keine echte Datei-I/O auf `target_files` — nur Projektion/Simulation.

**Failure-Mode (hypothetisch):**
Nach Step A (reale Mutation) ist der Dateiinhalt verändert — nicht durch
Locator-Drift, sondern durch vom Apply-Layer vorgenommene Normalisierungen oder
Nebeneffekte (z.B. Trailing-Newlines, BOM-Stripping). Ein Folge-Step, der
`exact_before` nutzt, würde an einem Hash-/Content-Mismatch scheitern, nicht
weil der Locator an eine andere Stelle zeigt, sondern weil der erwartete
Vorher-Zustand schlicht nicht mehr dem Ist-Zustand auf Disk entspricht.

**Trennung belegt / plausibel / offen:**
- belegt: Dry-Run simuliert kein echtes Datei-I/O (Code-Beleg in replay-gap-candidates.md)
- plausibel: Reale Apply-Layer können Normalisierungseffekte produzieren
- offen: Kein realer Ausführungsbeleg; keine kontrollierte Fixture geprüft

---

### RRG-02: Git-Working-Tree-Index-Effects (nicht real-run-belegt)

Quelle:
`experiments/2026-04-23_agent-failure-surface/results/replay-gap-candidates.md`
Spalte: `RRG-02 Git-Working-Tree-Index-Effects`

| Feld | Wert |
|------|------|
| Betroffene Achse | Git-Index / Working Tree, Reihenfolge realer Mutationen |
| Status in replay-gap-candidates.md | `intentional_gap` |
| Priorität | Phase F: nach RRG-01 |
| Real-Run-Beleg | **nicht vorhanden** |

**Beschreibung (aus replay-gap-candidates.md):**
Reale Mutationen können untracked/modified/indexed Nebenwirkungen haben.
Der Dry-Run bildet Git-Zustand nicht ab. `replay_minimal.py` kennt keine
`git`-Operationen; vorhandene Tests validieren JSON-Vertrag, nicht `git status`.

**Failure-Mode (hypothetisch):**
Nach Step A werden Änderungen ganz oder teilweise gestaged. Ein Folge-Step,
der auf dieselbe Datei zeigt, könnte gegen einen anderen Zustand arbeiten als
erwartet (staged vs. unstaged vs. committed). Der Drift liegt hier nicht im
Locator-Text, sondern in der Git-Sicht auf den Dateiinhalt. Kein Locator
driftet — der Locator könnte korrekt auflösen, aber auf den falschen
Datei-Snapshot zeigen.

**Trennung belegt / plausibel / offen:**
- belegt: Dry-Run hat kein Git-Modell (Code-Beleg in replay-gap-candidates.md)
- plausibel: Reale Runner mit Git-State-Aware-Umgebung können abweichen
- offen: Kein realer Ausführungsbeleg; keine kontrollierte Fixture geprüft

---

## Cross-Diagnosis-Matrix

Spalten:
- **Kandidat**: Remediation-Kandidat aus rrg03-remediation-strategy-comparison.md
- **RRG-03-Bezug**: Wie adressiert der Kandidat den belegten RRG-03-Drift?
- **RRG-01 mögliche Ursache**: Wie passt der Kandidat zur hypothetischen RRG-01-Ursache?
- **RRG-02 mögliche Ursache**: Wie passt der Kandidat zur hypothetischen RRG-02-Ursache?
- **Gleiche Remediation plausibel?**: Würde derselbe Kandidat für alle drei Gaps greifen?
- **Zusatzbeleg nötig?**: Welche Evidenz fehlt noch?
- **Risiko bei vorschnellem v0.2-Patch**: Was passiert, wenn der Kandidat ohne RRG-01/RRG-02-Beleg implementiert wird?

| Kandidat | RRG-03-Bezug | RRG-01 mögliche Ursache | RRG-02 mögliche Ursache | Gleiche Remediation plausibel? | Zusatzbeleg nötig? | Risiko vorschneller Patch |
|----------|-------------|------------------------|------------------------|-------------------------------|-------------------|--------------------------|
| **post_apply_anchor** | Adressiert Ursache: Locator-Position nach Apply neu verankert | Teilweise: verhindert Locator-Drift, aber nicht Disk-Content-Normalisierung | Nein: Git-Index-Drift ist eine andere Achse | Nein: Für RRG-01 und RRG-02 unvollständig | RRG-01 Real-Run, RRG-02 Real-Run | Anchor adressiert nur Positionsdrift; RRG-01/RRG-02-Ursachen bleiben offen |
| **byte_range** | Teilweise: stabiler Anker wenn byte-Offsets nach Apply aktualisiert werden | Nein: Line endings und Normalisierungen ändern byte-Offsets; würde falsch-negativ produzieren | Nein: Git-Index-Drift ist orthogonal zu byte_range | Nein: Für RRG-01 kontraproduktiv (byte-Offsets nach Normalisierung instabil) | RRG-01 Real-Run (zeigen ob byte_range nach Apply noch stimmig) | byte_range als Pflichtfeld bricht alle bestehenden Fixtures (keines hat byte_range/byte_start) |
| **exact_before hash / snapshot binding** | Teilweise: blockiert Step B bei Content-Mismatch; adressiert nicht Positionsdrift wenn Hash passt | Hoch: Hash-Binding deckt genau den RRG-01-Fall ab (Content-Normalisierung nach Apply würde Hash-Mismatch produzieren) | Nein: Git-Index-Drift liegt auf Datei-Snapshot-Ebene, nicht auf Locator-Ebene | Teilweise: stark für RRG-01, schwach für RRG-02 | RRG-01 Real-Run mit Hash-Binding-Probe | Bestehende Fixtures mit `exact_before` (String) benötigen SHA-256-Format-Änderung → breaking für jene |
| **re_resolution_required** | Adressiert Ursache: Folgekommando muss Locator erneut auflösen | Teilweise: würde Positionsdrift erzwingen zu erkennen, aber nicht Content-Normalisierungseffekte | Nein: Erneute Auflösung gegen Git-Index-Zustand nicht spezifiziert | Nein: Für RRG-01 unvollständig; für RRG-02 gar nicht adressiert | RRG-01 Real-Run, RRG-02 Real-Run | Als Pflichtfeld in Multi-Step-Chains: bricht alle existierenden validen Chains ohne `re_resolution_required` |
| **validator warning for multi-match locator** | Adressiert Symptom: Warnung wenn Locator mehr als einmal matcht | Nein: RRG-01-Ursache ist Content-Normalisierung, nicht Multi-Match | Nein: RRG-02-Ursache ist Git-State, nicht Multi-Match | Nein: Adressiert weder RRG-01 noch RRG-02 | RRG-01 und RRG-02 Real-Runs, aber irrelevant für diesen Kandidaten | Additive Warnung: geringstes Risiko; false positives bei legitimen Multi-Match-Scenarios |
| **runner-side resolver hardening** | Adressiert Symptom: Runtime neu-auflösen und Drift-Check | Teilweise: wenn hardening auch Content-Diff prüft | Teilweise: wenn hardening auch Git-State einbezieht | Möglicherweise ja (breitester Scope), aber außerhalb v0.1 | Allgemeiner Beleg für reale Runner-Korrektheit (viele Fixtures) | Scope-Drift hoch: weitet Patch über fixture_only hinaus aus; keine belegte Notwendigkeit |
| **no_patch_observe_more** | Zulässig: weitere Real-Runs abwarten | Korrekt: RRG-01 braucht Real-Run-Beleg bevor Remediation | Korrekt: RRG-02 braucht Real-Run-Beleg bevor Remediation | Ja: in dem Sinne, dass keine Remediation entschieden wird | Weitere Real-Runs für RRG-01 und RRG-02 | Kein Risiko; schließt andere Kandidaten nicht aus |

---

## Diagnose: Ursachenstruktur

### RRG-01 vs. RRG-03: Ähnlich — aber unterschiedliche Drift-Achse

**RRG-03** (belegt): Der Locator-Text existiert weiterhin im Dokument, aber nach
einer realen Step-A-Mutation verschiebt sich seine Position (anderer Match-Index,
andere Zeile). Ursache: Text-basierte Locator-Auflösung ohne erneute
Positionsverifizierung.

**RRG-01** (hypothetisch): Nicht die Locator-Position driftet, sondern der
Dateiinhalt selbst ändert sich durch Apply-Nebeneffekte (Normalisierungen,
line endings). Ein stabiler `exact_before`-Hash würde scheitern, aber der
Locator könnte auf die korrekte Zeile zeigen.

**Befund:**
- RRG-01 und RRG-03 teilen die Achse "post-apply state divergence".
- Die Failure-Mode unterscheiden sich: Positionsdrift (RRG-03) vs.
  Content-Normalisierungsdrift (RRG-01).
- `post_apply_anchor` und `re_resolution_required` greifen bei RRG-03;
  für RRG-01 wäre `exact_before hash/snapshot binding` primär relevant.
- **Gleiche Remediation-Klasse: nein.** Partial overlap, aber eigene
  Fixture-Probe nötig.

### RRG-02 vs. RRG-03: Ähnlich in Erscheinung — strukturell orthogonal

**RRG-03** (belegt): Locator-Drift auf Text-Ebene nach realer Mutation.

**RRG-02** (hypothetisch): Git-Working-Tree-Effekte. Nicht der Locator-Text
driftet, sondern die Git-Sicht auf die Datei. Ein Kommando könnte korrekt
auflösen, aber gegen einen gestaged oder falsch-eingestuften Datei-Snapshot
arbeiten.

**Befund:**
- RRG-02 und RRG-03 teilen das Setting "nach realer Mutation in Multi-Step-Chain".
- Die Ursachen sind orthogonal: Locator-Drift ist ein Text-Resolving-Problem;
  Git-Index-Drift ist ein Workspace-Management-Problem.
- Keiner der RRG-03-Remediation-Kandidaten adressiert Git-State-Tracking primär.
  `runner-side resolver hardening` könnte in einer breiten Implementierung
  Git-State einschließen, aber das wäre Scope-Drift über den belegten Befund hinaus.
- **Gleiche Remediation-Klasse: nein.** RRG-02 ist eine eigene Drift-Klasse.

---

## Remediation-Kandidaten gegen RRG-01/RRG-02

### post_apply_anchor

- **Für RRG-03**: Adressiert Ursache (Positionsdrift nach Apply).
- **Für RRG-01**: Teilweise — Anker verhindert Text-Positionsdrift. Normalisierungseffekte
  auf Disk-Content werden damit nicht erfasst.
- **Für RRG-02**: Nicht adressiert — Git-Index-Drift liegt außerhalb des Kandidaten-Scopes.
- **Fazit**: Nur partiell tauglich für RRG-01/RRG-02.

### byte_range

- **Für RRG-03**: Teilweise — stabiler Anker wenn byte-Offsets nach Apply neu berechnet.
- **Für RRG-01**: Kontraproduktiv — Normalisierungen (line endings, BOM) verschieben
  byte-Offsets. byte_range nach Apply ohne Re-Calculation wäre instabil.
- **Für RRG-02**: Nicht adressiert.
- **Breaking-Change-Risiko**: Derzeit kein einziges Fixture in `tests/fixtures/command_chains/`
  oder `tests/fixtures/agent_commands/write_change/` enthält `byte_range` oder `byte_start`.
  Als Pflichtfeld: alle bestehenden write_change-Fixtures werden ungültig.
- **Fazit**: Für RRG-01 potentiell kontraproduktiv; als Pflichtfeld breaking.

### exact_before hash / snapshot binding

- **Für RRG-03**: Teilweise — blockiert Step B wenn Hash mismatch, aber adressiert
  Positionsdrift nicht direkt.
- **Für RRG-01**: Stark relevant — SHA256-Hash des `exact_before`-Contents würde
  Content-Normalisierungseffekte direkt detektieren.
- **Für RRG-02**: Teilweise — wenn Hash über den staged/unstaged Inhalt gemessen;
  nicht spezifiziert welchen Snapshot der Hash binden soll.
- **Breaking-Change-Risiko**: Fixtures die derzeit `exact_before` als String haben
  (`valid-minimal.json` in command_chains: `"exact_before": "## Laufende Versuche\n"`),
  müssten in ein Hash-Format gewechselt werden. Bestehende Fixtures ohne `exact_before`
  sind nicht betroffen (Feld bleibt optional).
- **Fazit**: Stärkster Kandidat für RRG-01; bricht nur Fixtures die bereits `exact_before` nutzen.

### re_resolution_required

- **Für RRG-03**: Adressiert Ursache (zwingt erneute Auflösung nach jedem Apply).
- **Für RRG-01**: Teilweise — erneute Locator-Auflösung deckt Positionsdrift, aber
  nicht Content-Normalisierungseffekte.
- **Für RRG-02**: Nicht adressiert — erneute Locator-Auflösung betrifft Text-Position,
  nicht Git-Index-State.
- **Breaking-Change-Risiko**: Als Pflichtfeld in Multi-Step-Chains:
  - `valid-validate-with-write.json`: hat `locator: "def main"` ohne target_lines oder
    exact_before → würde re_resolution_required benötigen.
  - `valid-errors-with-check-prefix.json`: analog.
  - Alle bestehenden validen Chains ohne dieses Feld würden invalide.
- **Fazit**: Als opt-in: nicht-breaking; als Pflichtfeld: breaking für alle Multi-Step-Chains.

### validator warning for multi-match locator

- **Für RRG-03**: Adressiert Symptom (warnt bei Multi-Match, dem Vorboten des Drifts in Run 01+02).
- **Für RRG-01**: Nicht relevant — RRG-01-Ursache ist Content-Normalisierung, kein Multi-Match.
- **Für RRG-02**: Nicht relevant — RRG-02-Ursache ist Git-State.
- **Breaking-Change-Risiko**: Nur Warnung (kein Fehler) → additiv, non-breaking.
  False-Positive-Risiko: Fixtures mit legitimem Multi-Match (z.B. `"locator": "def main"`
  in einer Datei mit mehreren `def main`-Vorkommen) würden Warnung produzieren.
- **Fazit**: Additiv möglich, kein breaking change, aber nur für RRG-03-Symptom relevant.

### runner-side resolver hardening

- **Für RRG-03**: Adressiert Symptom (Runtime-Neuauflösung nach Apply).
- **Für RRG-01**: Möglicherweise teilweise — wenn hardening auch Disk-Content-Diff prüft.
- **Für RRG-02**: Möglicherweise teilweise — wenn hardening auch Git-State einschließt.
- **Breaking-Change-Risiko**: Eingriff in `tools/vibe-cli/replay_minimal.py` — per
  Aufgabenstellung explizit verboten (Diagnose-only). Hohe Scope-Drift.
- **Fazit**: Deferred; außerhalb v0.1 und außerhalb dieses Diagnose-Scopes.

### no_patch_observe_more

- **Für RRG-01**: Korrekt — kein Real-Run-Beleg vorhanden.
- **Für RRG-02**: Korrekt — kein Real-Run-Beleg vorhanden; RRG-02 hat in
  replay-gap-candidates.md Status `intentional_gap`.
- **Fazit**: Für RRG-01 und RRG-02 aktuell die epistemisch sauberste Position.

---

## Breaking-Change-Scan

### Fixture-Inventur: Locator-Stabilität

Geprüfte Pfade:
- `tests/fixtures/command_chains/`
- `tests/fixtures/agent_commands/write_change/`
- `tests/fixtures/agent_handoff/`
- `experiments/2026-04-23_agent-failure-surface/artifacts/*/fixtures/`

**Ergebnis:**

| Fixture-Set | Gesamt write_change | mit exact_before | mit target_lines | mit byte_range | ohne alle drei |
|-------------|--------------------:|---------------:|----------------:|---------------:|--------------:|
| command_chains (valid) | 3 | 1 | 0 | 0 | 2 |
| command_chains (invalid) | 16 | 2 | 0 | 0 | 14 |
| agent_commands/write_change (valid) | 3 | 2 | 1 | 0 | 0 |
| experiment/run-phase-f-rrg03-real fixtures | 2 | 1 | 0 | 0 | 1 |
| experiment/run-phase-f-rrg03-real-02 fixtures | 2 | 1 | 0 | 0 | 1 |

**Feststellung:** Kein einziges Fixture enthält `byte_range` oder `byte_start`.
Die Mehrheit der write_change-Fixtures nutzt weder `exact_before`, `target_lines`
noch `byte_range`.

### Kandidaten: additiv vs. breaking

| v0.2-Kandidat | Art der Änderung | Breaking-Change-Risiko | Betroffene Fixtures |
|---------------|-----------------|------------------------|---------------------|
| post_apply_anchor (optional) | additiv | nein | — |
| post_apply_anchor (required in multi-step) | breaking | ja | alle validen Chains mit write_change |
| byte_range (optional) | additiv | nein | — |
| byte_range (required) | breaking | ja | alle write_change-Fixtures (100%) |
| exact_before hash (opt-in, ersetzt String) | breaking für bestehende | für Fixtures die bereits exact_before haben | valid-minimal.json (command_chains), valid-edge-remove.json, pass-with-exact-before-after.json (handoff) |
| exact_before hash (neues Feld, additiv) | additiv | nein | — |
| re_resolution_required (optional, deklarativ) | additiv | nein | — |
| re_resolution_required (required in multi-step) | breaking | ja | valid-validate-with-write.json, valid-errors-with-check-prefix.json |
| validator warning multi-match | additiv | nein | false positives möglich |
| runner-side resolver hardening | Runtime-Patch | außerhalb Diagnose-Scope | alle Chains |

### Fixtures ohne stabile Locator-Sicherung

Folgende **valide** Fixtures haben einen `locator`-String ohne `exact_before`,
`target_lines` oder `byte_range` — sie würden in einem realen Multi-Step-Szenario
anfällig für RRG-03-artigen Drift sein:

- `tests/fixtures/command_chains/valid-validate-with-write.json`:
  `locator: "def main"` — generischer Bezeichner, potentiell multi-match in Python-Dateien
- `tests/fixtures/command_chains/valid-errors-with-check-prefix.json`:
  `locator: "def main"` — identisch wie oben

Diese Fixtures sind **valide unter v0.1** (Locator als optionaler Anker, nicht stabiler
Identifier). Unter einem v0.2-Regime mit `re_resolution_required` oder Pflicht-`exact_before`
würden sie invalide werden.

---

## Ergebnisstatus

```
RRG-01/RRG-02 partially overlap but need separate fixture proof
```

**Begründung:**

1. RRG-01 (Disk-State-Apply-Delta) teilt mit RRG-03 die Achse "post-apply state divergence",
   aber der Failure-Mode ist verschieden: Content-Normalisierung (RRG-01) vs.
   Locator-Positionsdrift (RRG-03). `exact_before hash/snapshot binding` ist der stärkste
   Kandidat für RRG-01, während für RRG-03 `post_apply_anchor` und `re_resolution_required`
   stärker sind.

2. RRG-02 (Git-Working-Tree-Index-Effects) ist strukturell orthogonal zu RRG-03.
   Die Git-Index-Drift-Achse wird durch keinen der RRG-03-orientierten Remediation-Kandidaten
   primär adressiert. RRG-02 bildet eine eigene Drift-Klasse.

3. Keiner der RRG-03-Remediation-Kandidaten ist ohne eigenen Fixture-Beleg für RRG-01 oder
   RRG-02 als hinreichend einzustufen. `no_patch_observe_more` ist für beide die aktuell
   epistemisch sauberste Position.

**Kein finaler Gewinner. Kein accepted decision. Kein Patch.**

---

## Empfehlung für nächste Schritte

1. **RRG-01 Real-Run**: Kontrollierte Fixture mit realem Write und Normalisierungseffekt
   (z.B. trailing-newline-Varianz). Beobachten, ob `exact_before`-Binding bricht während
   Locator-Position stabil bleibt.

2. **RRG-02 Real-Run**: Kontrollierter Workspace mit Git-State-Assertions nach Step A.
   Beobachten, ob Git-Index-Zustand Folge-Steps beeinflusst.

3. **Breaking-Change-Entscheidung**: Vor jeder v0.2-Implementierung mit `byte_range`,
   `re_resolution_required` (as required) oder `exact_before`-Hash-Format-Änderung
   muss die Fixture-Corpus-Kompatibilität geprüft werden. Additiv-optionale Einführung
   dieser Felder ist non-breaking.

4. **Nicht jetzt**: Decision Preimage, Status-Aufwertung, Runtime-Patch.

---

## Nicht-Ziele dieses Dokuments

- Keine Runtime-/Schema-/Validator-/CI-Änderung.
- Keine Aufwertung von `decisions/process/2026-04-30-rrg03-remediation-boundary.yml`
  von `proposed` auf `accepted`.
- Kein Decision Preimage.
- Keine v0.2-Implementierung.
- Kein neuer CI-Gate.
- Keine historischen Artifact-Rewrites.
