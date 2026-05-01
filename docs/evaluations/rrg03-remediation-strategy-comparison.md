---
title: "RRG-03 Remediation Strategy Comparison"
status: draft
canonicality: operative
created: "2026-04-30"
updated: "2026-05-01"
relations:
  - type: references
    target: "../../experiments/2026-04-23_agent-failure-surface/artifacts/run-phase-f-rrg01-real/observed.json"
  - type: references
    target: "../../experiments/2026-04-23_agent-failure-surface/artifacts/run-phase-f-rrg02-real/observed.json"
  - type: references
    target: "../../experiments/2026-04-23_agent-failure-surface/artifacts/run-phase-f-rrg03-real/observed.json"
  - type: references
    target: "../../experiments/2026-04-23_agent-failure-surface/artifacts/run-phase-f-rrg03-real-02/observed.json"
  - type: references
    target: "../../experiments/2026-04-23_agent-failure-surface/results/phase-f-rrg03-locator-drift.md"
  - type: references
    target: "../../decisions/process/2026-04-30-rrg03-remediation-boundary.yml"
  - type: references
    target: "../../contracts/command-semantics.md"
---

# RRG-03 Remediation Strategy Comparison

## These / Antithese / Synthese

**These:** RRG-03 ist fixture-spezifisch belegt und das Patch-Gate ist ausgelöst.

**Antithese:** Der Beleg entscheidet nicht automatisch die technische Remediation.
Das Patch-Gate signalisiert Handlungsbedarf, nicht eine spezifische Lösung.

**Synthese:** v0.2 braucht einen Strategie-Vergleich vor jedem Schema-,
Validator- oder Runtime-Eingriff. Die Kandidaten müssen gegen denselben
Ist-Zustand bewertet werden, der den Befund erzeugt hat.

---

## Belegter Ist-Zustand

Alle drei RRGs sind seit 2026-05-01 fixture-proven. Quellen:

- `experiments/2026-04-23_agent-failure-surface/artifacts/run-phase-f-rrg01-real/observed.json`
- `experiments/2026-04-23_agent-failure-surface/artifacts/run-phase-f-rrg02-real/observed.json`
- `experiments/2026-04-23_agent-failure-surface/artifacts/run-phase-f-rrg03-real/observed.json`
- `experiments/2026-04-23_agent-failure-surface/artifacts/run-phase-f-rrg03-real-02/observed.json`
- `experiments/2026-04-23_agent-failure-surface/results/phase-f-rrg03-locator-drift.md`
- `decisions/process/2026-04-30-rrg03-remediation-boundary.yml`

| RRG | classification | patch_gate.triggered | proof_scope | Drift-Achse |
|-----|----------------|----------------------|-------------|-------------|
| RRG-01 | `content_drifted` | true | fixture_only | Content-/Snapshot-Drift durch Apply-Layer-Normalisierung (CRLF→LF) |
| RRG-02 | `git_state_drifted` | true | fixture_only | Git-State-Drift: HEAD / Index / Working Tree divergieren nach staged + unstaged Mutation |
| RRG-03 (Run 01) | `drifted` | true | fixture_only | Locator-Positionsdrift: Removal-Drift, Index-0 rückt nach unten |
| RRG-03 (Run 02) | `drifted` | true | fixture_only | Locator-Positionsdrift: Injection-Before-Drift, neuer Treffer verdrängt Index-0 |

Allgemeine Runner-Sicherheitsaussagen sind aus keinem dieser Fixture-Belege ableitbar.
Jeder Beleg gilt ausschließlich für die jeweilige kontrollierte Fixture (proof_scope=fixture_only).
Die aktuelle Boundary bleibt: proposed, kein Patch.

**RRG-03 Detail:** Nach realer Step-A-Mutation (C2) driftet der Step-B-Locator
`"Validate token"` von C1 Zeile 4 (byte 33–47) auf C3 Zeile 7 (byte 81–95)
(Run 01). Run 02 bestätigt dasselbe Muster über einen anderen Mechanismus
(Injection-Before).

---

## Kandidatenmatrix

| # | Kandidat | Beschreibung |
|---|----------|--------------|
| 1 | **post_apply_anchor** | Nach jedem Apply-Schritt wird ein Anker (z.B. Zeilennummer + Hash-Snapshot) festgeschrieben, der als Ausgangspunkt für die nächste Resolution dient. |
| 2 | **byte_range** | Das Kommando enthält neben dem lesbaren Locator auch einen byte_start/byte_end-Anker, der nach Step A neu ausgewertet wird. |
| 3 | **exact_before hash / snapshot binding** | `exact_before` wird durch einen SHA256-Hash des Kontexts gebunden; Mismatch blockiert Step B sofort. |
| 4 | **explicit re_resolution_required** | Kommandokette deklariert explizit, dass nach jedem Apply eine erneute Resolution für Folgekommandos nötig ist. Verletzung = Fehler. |
| 5 | **validator warning for multi-match locator** | Validator warnt, wenn ein Locator innerhalb einer Chain mehr als einmal matcht und kein post_apply_anchor gesetzt ist. |
| 6 | **runner-side resolver hardening** | Runtime-Patch in `tools/vibe-cli/replay_minimal.py`: nach jedem Apply wird der Locator erneut aufgelöst und ein Drift-Check durchgeführt. |
| 7 | **no_patch_observe_more** | Keine semantische, validatorische oder Runtime-Änderung; weitere Real-Runs abwarten, bevor eine Remediation entschieden wird. |

---

## Bewertungskriterien

| Kriterium | Erläuterung |
|-----------|-------------|
| Adressiert Ursache? | Drift entsteht aus schwacher Folgeadressierung. Behebt der Kandidat das semantisch? |
| Maschinell prüfbar? | Kann die Invariante automatisch geprüft werden (Schema, Validator, CI)? |
| Rückwärtskompatibilität | Bricht der Kandidat bestehende Chains oder Fixtures? |
| Risiko falsch-positiver Signale | Kann der Kandidat Drift-Alarm auslösen, wo keiner vorliegt? |
| Scope-Drift | Weitet der Kandidat den Patch-Scope über fixture_only hinaus aus? |
| Aufwand | Relative Einschätzung des Implementierungsaufwands. |
| Verhältnis zu command-semantics v0.1 | Schärft der Kandidat die bestehende Semantik oder bricht er sie? |
| Benötigte Zusatzbelege | Welche weiteren Real-Runs oder Diagnosen sind Voraussetzung? |

### Kandidatenbewertung

| Kandidat | Ursache? | Maschinell? | Rückwärtskomp. | Falsch-positiv | Scope-Drift | Aufwand | v0.1-Verhältnis | Zusatzbelege |
|----------|----------|-------------|----------------|----------------|-------------|---------|-----------------|--------------|
| post_apply_anchor | ja | ja (Schema) | mittel | niedrig | niedrig | mittel | schärft | RRG-03 Run 01+02 erledigt; RRG-01 fixture_proven (content_drifted); RRG-02 fixture_proven (orthogonal; nicht adressiert) |
| byte_range | teilweise | ja (Schema) | niedrig (breaking) | niedrig | niedrig | hoch | bricht | mehrere Fixtures |
| exact_before hash | teilweise | ja (Validator) | mittel | niedrig | niedrig | mittel | schärft | RRG-03 Run 01+02 erledigt; RRG-01 stärkster Kandidat; RRG-02 orthogonal |
| re_resolution_required | ja | ja (Schema+Validator) | mittel | niedrig | niedrig | niedrig | schärft | RRG-03 Run 01+02 erledigt; RRG-01 fixture_proven (teilweise); RRG-02 fixture_proven (nicht adressiert) |
| validator multi-match | nein (Symptom) | ja (Validator) | hoch | mittel | niedrig | niedrig | schärft | RRG-03 Run 01+02 erledigt; RRG-01/RRG-02 nicht relevant für diesen Kandidaten |
| runner hardening | nein (Symptom) | nein | hoch | mittel | hoch | hoch | außerhalb v0.1 | viele Fixtures, allg. Beleg |
| no_patch_observe_more | nein | nein | hoch | keines | keines | keines | neutral | weitere Real-Runs |

---

## Vorläufiges Ergebnis

**Kein finaler Gewinner.**

Wahrscheinlicher Leitkandidat für RRG-03: command-contract-first mit `post_apply_anchor`
oder `re_resolution_required` als zu prüfende Hypothese. Beide adressieren
die Ursache (schwache Folgeadressierung) semantisch und sind maschinell
prüfbar, ohne den Patch-Scope über den belegten Fixture-Befund hinaus
auszuweiten.

**RRG-01-spezifisch:** `exact_before hash/snapshot binding` ist der stärkste
Kandidat — Content-/Snapshot-Drift durch Apply-Layer-Normalisierung (CRLF→LF)
wird direkt durch Hash-Mismatch erkannt. `post_apply_anchor` und
`re_resolution_required` adressieren RRG-01 nur teilweise (sie decken
Positionsdrift, nicht Content-Normalisierungseffekte).

**RRG-02-spezifisch:** Kein aktueller Kandidat adressiert Git-State-Drift primär.
RRG-02 ist strukturell orthogonal zu RRG-01 und RRG-03: Die Drift-Achse ist
Workspace-Management (HEAD / Index / Working Tree), nicht Text-Resolving.
Reine Locator-Remediation löst RRG-02 nicht. RRG-02 braucht Git-State-Snapshot-Semantik,
die in keinem der sieben Kandidaten explizit enthalten ist.

**Breaking-Change-Grenzen:**
- `byte_range` als required-Feld bleibt breaking (kein einziges bestehendes Fixture enthält es).
- Additive optionale Felder (`post_apply_anchor`, `re_resolution_required`, `exact_before hash`
  als neues Feld) bleiben non-breaking.
- `exact_before` als Hash-Format-Wechsel (statt String) bricht Fixtures, die bereits
  `exact_before` als String haben.

`runner-side resolver hardening` und `validator warning for multi-match locator`
bleiben deferred: Sie adressieren Symptome, nicht die Ursache, und benötigen
einen allgemeineren Beleg, den die aktuellen Real-Runs (fixture_only) nicht
liefern.

`no_patch_observe_more` bleibt zulässig und ist mit allen anderen Kandidaten
kombinierbar.

**Kein accepted decision status** — dieser Vergleich ist Grundlage für ein
Decision Preimage, nicht für eine abgeschlossene Entscheidung.

---

## Erforderliche nächste Belege

1. ~~Mindestens ein zusätzlicher Real-Run für RRG-03 mit alternativer Fixture
   (anderer Locator, anderes Dokument, anderes Drift-Muster).~~ ✓ Erledigt: Run 02
2. ~~Separate Diagnose, ob RRG-01 und RRG-02 denselben Remediation-Pfad
   benötigen oder ob ihre Drift-Ursachen abweichen.~~ ✓ Erledigt: Diagnose-Dokument erstellt;
   RRG-01 fixture_proven (content_drifted, 2026-05-01, Artefakt: run-phase-f-rrg01-real/observed.json);
   RRG-02 fixture_proven (git_state_drifted, 2026-05-01, Artefakt: run-phase-f-rrg02-real/observed.json).
3. ~~Prüfung, ob v0.2 einen Breaking Change für bestehende Chains bedeutet —
   insbesondere bei `byte_range` und `re_resolution_required`.~~ ✓ Erledigt: Breaking-Change-Scan
   in Cross-Diagnosis-Dokument (replay-gap-cross-diagnosis-rrg01-rrg02.md).
4. Erst danach: Decision Preimage auf Basis dieses Strategie-Vergleichs und
   der zusätzlichen Belege.

---

## Zusatzbeleg Run 02 (Injection-Before Pattern)

Quelle: `experiments/2026-04-23_agent-failure-surface/artifacts/run-phase-f-rrg03-real-02/observed.json`

Run 02 prüft ein anderes Drift-Muster als Run 01:

| | Run 01 | Run 02 |
|---|---|---|
| Fixture | Auth Flow Notes, Locator "Validate token" | API Gateway Notes, Locator "Process request" |
| Drift-Muster | Removal-drift: erster Treffer entfernt | Injection-before-drift: neuer Treffer eingefügt oberhalb |
| match_count C1→C3 | 2→1 | 3→4 |
| C1 line | 4 | 7 |
| C3 line | 7 | 4 |
| Klassifikation | drifted | drifted |
| Patch-Gate | TRIGGERED | TRIGGERED |

**Befund:** Beide Fixtures bestätigen `classification=drifted` und `patch_gate.triggered=true`.
Die Drift-Ursache ist dieselbe (schwache Folgeadressierung), tritt aber durch
zwei verschiedene Mechanismen auf:
- Run 01: Treffer-Reduktion verschiebt Index-0-Auswahl nach unten.
- Run 02: Treffer-Injektion verschiebt Index-0-Auswahl nach oben.

**Auswirkung auf Bewertungsmatrix:** Die Kandidatenbewertung ändert sich nicht
grundlegend. Beide Runs stärken die Einschätzung, dass `post_apply_anchor` und
`re_resolution_required` die Ursache adressieren (sie würden in beiden
Drift-Mustern greifen), während `runner-side resolver hardening` und
`validator warning for multi-match locator` weiterhin deferred bleiben
(sie adressieren Symptome, nicht die Ursache).

**Kein finaler Gewinner.** Zwei Messpunkte sind stärker als einer, aber kein
Beweis für allgemeine Locator-Unsicherheit jenseits kontrollierter Fixtures.
Scope-Boundary: `proof_scope=fixture_only` gilt für beide Runs.

---

## Cross-Diagnosis Status

Quelle: `docs/evaluations/replay-gap-cross-diagnosis-rrg01-rrg02.md`

| Befund | Stand |
|--------|-------|
| Diagnose RRG-01 vs. RRG-03-Kandidaten | abgeschlossen (Diagnose-only) |
| Diagnose RRG-02 vs. RRG-03-Kandidaten | abgeschlossen (Diagnose-only) |
| RRG-01 Real-Run | fixture_proven (2026-05-01): content_drifted |
| RRG-02 Real-Run | fixture_proven (2026-05-01): git_state_drifted |

**Diagnosebefund (zusammengefasst):**

> `RRG-01/RRG-02 partially overlap and are now separately fixture-proven`

- RRG-01 teilt mit RRG-03 die Achse "post-apply state divergence", hat aber
  einen anderen Failure-Mode (Content-Normalisierung statt Locator-Positionsdrift).
  Stärkster Kandidat für RRG-01: `exact_before hash/snapshot binding`.
  Beleg: `run-phase-f-rrg01-real/observed.json`, classification=content_drifted.
- RRG-02 ist strukturell orthogonal zu RRG-03 (Git-Index-Drift vs. Text-Locator-Drift).
  Keiner der aktuellen Kandidaten adressiert RRG-02 primär; RRG-02 wird NICHT durch
  reine Locator-Remediation gelöst.
  Beleg: `run-phase-f-rrg02-real/observed.json`, classification=git_state_drifted.
- Breaking-Change-Scan: `byte_range` und `re_resolution_required` als Pflichtfelder
  würden alle bestehenden validen Chains brechen. Additiv-optionale Einführung ist non-breaking.

**Offene Punkte (aktualisiert):**

1. ~~Mindestens ein zusätzlicher Real-Run für RRG-03 mit alternativer Fixture.~~ ✓ Erledigt: Run 02
2. ~~Separate Diagnose, ob RRG-01 und RRG-02 denselben Remediation-Pfad benötigen.~~ ✓ Erledigt: Diagnose-Dokument erstellt; RRG-01 fixture_proven (content_drifted, 2026-05-01); RRG-02 fixture_proven (git_state_drifted, 2026-05-01).
3. ~~Prüfung, ob v0.2 einen Breaking Change für bestehende Chains bedeutet.~~ ✓ Erledigt: Breaking-Change-Scan in Diagnose-Dokument.
4. Erst danach: Decision Preimage auf Basis dieses Strategie-Vergleichs und der zusätzlichen Belege.

---

## Belegt / Plausibel / Offen

### Belegt (fixture-spezifisch)

- RRG-01: CRLF→LF-Normalisierung durch Apply-Layer produziert `content_drifted`
  (`exact_before` mit `\r\n` findet keinen Match nach LF-Write). Fixture-only.
  Artefakt: `run-phase-f-rrg01-real/observed.json`.
- RRG-02: Staged + unstaged Mutation auf derselben Datei produziert `git_state_drifted`
  (drei unterscheidbare Snapshots: HEAD / Index / Working Tree). Fixture-only.
  Artefakt: `run-phase-f-rrg02-real/observed.json`.
- RRG-03 (Run 01): Removal-Drift nach realer Mutation produziert Locator-Positionsdrift
  (C1 Zeile 4 → C3 Zeile 7). Fixture-only. Artefakt: `run-phase-f-rrg03-real/observed.json`.
- RRG-03 (Run 02): Injection-Before-Drift produziert entgegengesetzte Locator-Positionsdrift
  (C1 Zeile 7 → C3 Zeile 4). Fixture-only. Artefakt: `run-phase-f-rrg03-real-02/observed.json`.

### Abgeleitet / Remediation-Hypothesen

Diese Aussagen folgen logisch aus den Fixture-Belegen, sind aber keine Implementierungsbelege:
kein Schema-, Validator- oder Runtime-Patch wurde getestet. Sie sind Hypothesen für ein
späteres Decision Preimage.

- Aus RRG-01 folgt plausibel: `exact_before hash/snapshot binding` ist ein starker Kandidat
  für Content-/Snapshot-Drift — Hash-Mismatch würde CRLF→LF-Normalisierungseffekte direkt
  aufdecken.
- Aus RRG-03 folgt plausibel: `post_apply_anchor` und `re_resolution_required` sind starke
  Kandidaten für Locator-Positionsdrift — sie würden in beiden belegten Drift-Mustern
  (Removal, Injection-Before) greifen.
- Aus RRG-02 folgt plausibel: reine Locator-Remediation reicht nicht; Git-State-Snapshot-Semantik
  wird als eigenständiger Remediation-Pfad benötigt, der in keinem der sieben Kandidaten
  explizit enthalten ist.
- Breaking-Change-Abschätzung (aus Cross-Diagnosis-Scan, nicht runtime-geprüft): additive
  optionale Felder sind non-breaking; `byte_range` und `re_resolution_required` als Pflichtfelder
  würden alle bestehenden validen Chains brechen. Siehe Breaking-Change-Grenzen im Abschnitt
  „Vorläufiges Ergebnis".

### Plausibel (Übertragbarkeit auf ähnliche Runner-Szenarien)

- Andere Normalisierungsarten (trailing whitespace, BOM, encoding conversions) würden
  ähnlichen Content-Drift wie RRG-01 erzeugen — nicht durch diesen Run belegt.
- Andere Git-Workspace-Szenarien (untracked files, merge states, rebase mid-run) würden
  ähnlichen Git-State-Drift wie RRG-02 erzeugen — nicht durch diesen Run belegt.
- Die RRG-03-Drift-Mechanismen (Removal, Injection-Before) dürften in ähnlichen
  Runner-Szenarien auftreten — nicht durch diese Fixtures allgemein bewiesen.

### Offen

- Konkrete Runtime-Implementierung einer Remediation (kein Schema/Validator/CI geändert).
- Contract-Änderung für v0.2 (kein Decision Preimage gesetzt).
- Wahl des autoritativen Git-Snapshots für Runner-Implementierungen (HEAD / Index / WT).
- Hash-Format-Migration für bestehende `exact_before`-Fixtures (breaking, kein Plan).

**Die Beleglage reicht jetzt für einen späteren Decision Preimage,
aber das Decision Preimage wird durch dieses Dokument nicht gesetzt.**

---

## Nicht-Ziele dieses Dokuments

- Keine Runtime-/Schema-/Validator-/CI-Änderung.
- Keine Aufwertung von
  `decisions/process/2026-04-30-rrg03-remediation-boundary.yml`
  von `proposed` auf `accepted`.
- Keine v0.2-Implementierung.
- Kein neuer CI-Gate.
