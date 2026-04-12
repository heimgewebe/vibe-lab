---
title: "Blaupause: Execution-Bound Epistemics für Vibe-Lab"
status: draft
canonicality: operative
relations:
  - type: informs
    target: ../masterplan.md
schema_version: "0.1.0"
created: "2026-04-12"
updated: "2026-04-12"
author: "heimgewebe"
tags:
  - blueprint
  - execution
  - epistemics
---

# Blaupause: Execution-Bound Epistemics für Vibe-Lab

> **Hinweis:** Dies ist ein Entwurfsdokument (Blaupause). Es beschreibt Zielarchitektur und Härtungsvorschläge für das System, ist aber noch nicht als bindende Wahrheit umgesetzt. Verbindlichkeit entsteht erst durch spätere, technische Folge-PRs.


## 0. Kurzdefinition

**Begriff:** Blaupause

**Etymologie:** „Blaupause“ kommt aus der historischen Kopiertechnik des Cyanotypie-Verfahrens, bei dem technische Zeichnungen als weiße Linien auf blauem Grund vervielfältigt wurden. Bedeutung heute: ein präziser Bauplan, der nicht bloß Idee, sondern umsetzbare Struktur liefert.

**Begriff:** Execution-Bound Epistemics

**Etymologie:**
- execution ← lateinisch exsequi / executio = ausführen, zu Ende führen
- bound = gebunden
- epistemics ← griechisch epistēmē = Wissen, Erkenntnis

**Arbeitsdefinition:**
Wissen im Repo ist nur dann als „durchgeführt“ oder „entscheidungsfähig“ gültig, wenn es an reale, prüfbare Ausführungsspuren gebunden ist.

⸻

## 1. Zielbild

Vibe-Lab soll künftig vier Dinge sauber unterscheiden:
1. **Idee**
   noch kein Experiment, nur Hypothese oder Spur
2. **Design**
   Experiment ist geplant, aber noch nicht ausgeführt
3. **Execution**
   reale Durchführung mit maschinell prüfbaren Spuren
4. **Decision**
   Auswertung; harte Adoption immer auf Basis echter Execution-Artefakte (nicht jede Entscheidung ist eine Adoption)

**Zentralregel:**
Was nicht ausgeführt wurde, darf nicht wie Erkenntnis aussehen. Keine Adoption ohne Ausführung.

Das Repo soll also nicht nur gute Dokumente erzeugen, sondern falsche epistemische Aufwertung strukturell verhindern.

⸻

## 2. Problemraum präzise

### 2.1 Was gerade schieflaufen kann

Ein Agent kann heute:
- manifest.yml anlegen
- evidence.jsonl schreiben
- result.md formulieren
- sogar decision.yml erzeugen

…ohne je:
- einen Benchmark auszuführen,
- Tests zu starten,
- Logs zu erzeugen,
- Artefakte zu hinterlassen.

Dann entsteht synthetische Erkenntnis.

### 2.2 Warum das systemisch gefährlich ist

Das Problem ist nicht nur ein einzelnes falsches Experiment.
Es ist schlimmer:
- Entscheidungen referenzieren simulierte Evidenz
- Katalogeinträge können auf phantomhaften Experimenten beruhen
- das Repo trainiert sich darauf, Plausibilität mit Durchführung zu verwechseln

Das ist die eigentliche Katastrophe:

Nicht Halluzination an sich, sondern institutionalisierte Halluzination.

⸻

## 3. Architekturprinzipien

### 3.1 Trennung von Zuständen

Ein Experiment darf nie zugleich alles sein. Es gibt eine Trennung zwischen dem konzeptionellen Lebenszyklus und dem konkret modellierten Status.

Konzeptionelle Lebenszykluszustände:
- designed
- executing
- executed
- replicated
- reconstructed
- analyzed
- adopted
- rejected
- inconclusive

Davon wird im Manifest (`execution_status`) zunächst nur die execution-bezogene Teilmenge modelliert:
- designed
- executed
- replicated
- reconstructed

Zustände wie `analyzed`, `adopted`, `rejected` gehören zur breiteren Prozesslogik und nicht zwingend in das Feld `execution_status`.

### 3.2 Keine Entscheidung ohne Ausführung

Die Zulässigkeit von `decision.yml` hängt vom Entscheidungstyp ab:
- `execution_assessment` ist auch ohne echte Run-Spur zulässig (z.B. für `designed`).
- `adoption_assessment` ist **nur** zulässig, wenn mindestens eine echte Execution-Spur existiert.

### 3.3 Keine Ausführung ohne Proof

Ein executed-Status ist nur zulässig, wenn:
- Run-Events vorhanden sind
- mindestens ein Artefakt referenziert wird
- mindestens ein maschinell prüfbarer Output existiert

### 3.4 Observation ist nicht Execution

Qualitative Beobachtungen bleiben wertvoll, aber:
- sie zählen als observation
- nicht als proof of execution

### 3.5 Frühphase bleibt möglich

raw-vibes/ und designed-Experimente bleiben erlaubt.
Das System soll Exploration nicht verbieten, sondern epistemisch korrekt labeln.

⸻

## 4. Zielarchitektur im Repo

### 4.1 Zustandsmodell pro Ebene

**A) raw-vibes/**
- Ideen
- Fragmente
- Hypothesen
- noch keine Durchführungsbehauptung

**B) experiments/<name>/**

Mögliche substanzielle Zustände:
- designed
  geplant, aber nicht ausgeführt
- executed
  mindestens ein echter Run belegt
- reconstructed
  aus Vorwissen, Altmaterial, Erinnerungen oder nachgetragenen Spuren rekonstruiert, aber kein vollwertiger Execution-Proof. Rekonstruktion dokumentiert Vergangenheitsnähe, nicht Durchführungsbeweis. Was rekonstruiert ist, darf informativ sein, aber nicht proof-äquivalent. Rekonstruierte Run-Artefakte sind historische Hinweise und dürfen nie den Validatorpfad für `executed` erfüllen oder Grundlage eines `adoption_assessment` sein.
- analyzed
  Ergebnisse zusammengeführt
- adopted / rejected / inconclusive
  Entscheidung auf Basis vorhandener Ausführung

**C) catalog/, prompts/adopted/**

Nur aus adopted + nachweisbar ausgeführten Experimenten

⸻

## 5. Neue epistemische Verträge

### 5.1 Contract 1: Statusvertrag

**Regel**

manifest.yml bekommt einen Ausführungsstatus, getrennt vom Forschungsstatus.

**Vorschlag:**

```yaml
experiment:
  status: testing
  execution_status: designed
```

**Semantik**
- status = fachlicher Prozesszustand
- execution_status = tatsächlicher Durchführungszustand

**Erlaubte Werte**

```yaml
execution_status:
  - designed
  - executed
  - replicated
  - reconstructed
```

**Warum getrennt?**

Weil „testing“ aktuell im Repo oft überladen ist.
„Testing“ sagt nicht, ob etwas real lief, nur dass es in einem Prüfkontext steht.

⸻

### 5.2 Contract 2: Proof-of-Execution-Vertrag

Ein Experiment gilt nur dann als executed, wenn mindestens Folgendes vorliegt:

**Mindestanforderung (Proof-Bündel)**
Ein relevanter Run-Proof muss robust sein. Er besteht aus:
- `event_type`: "run" in `evidence.jsonl`
- `artifact_ref`: Muss ein String sein, relativ zum Experiment-Root, und auf eine physisch existierende Datei zeigen. Darf nicht absolut sein.
- `command`: Der exakte Ausführungsbefehl.
- `exit_code`: Oder ein äquivalenter technischer Ergebnisstatus.

Optional ergänzend: `duration`, `runner`, `trace_id`, `checksum/hash`.
Ein einzelnes Artefakt ohne dieses Bündel ist zu leicht als scheinbarer Beweis missbrauchbar.

**Minimales Beispiel**

```json
{"event_type":"run","timestamp":"2026-04-12T10:10:00Z","iteration":1,"metric":"execution","value":"completed","context":"benchmark: legacy-refactoring-v1","notes":"Ran benchmark script with spec-first prompt","command":"python3 tools/run_benchmark.py --challenge legacy-refactoring-v1 --mode spec-first","exit_code":0,"artifact_ref":"results/artifacts/run-001.log"}
```

⸻

### 5.3 Contract 3: Decision-Vertrag

Ein `adoption_assessment` in `results/decision.yml` ist nur erlaubt, wenn:
- execution_status ∈ {executed, replicated}
- evidence.jsonl mindestens ein run-Event enthält
- artifact_ref existiert und pfadsicher ist
- result.md auf reale Run-Artefakte Bezug nimmt

Andere Decision-Typen (wie `execution_assessment`) sind stattdessen zu nutzen, wenn kein echter Run vorliegt.

⸻

### 5.4 Zweite Wahrheitsachse: Contract-Treue

Eine echte Ausführung genügt nicht automatisch. Bei benchmark-basierten Experimenten muss zusätzlich gelten:
- Die benchmark-definierenden Invarianten wurden eingehalten.
- Das Verhalten wurde nicht unbemerkt verfälscht.

Execution Proof ohne Benchmark-Treue erzeugt nur Aktivität, keine belastbare Vergleichbarkeit.

⸻

## 6. Evidence-Modell: konkret

### 6.1 Eventtypen sauber trennen

Ich empfehle folgende Eventtypen:

- observation  = qualitative Beobachtung
- run          = reale Ausführung
- measurement  = messbarer numerischer oder kategorialer Wert aus realem Lauf (Feldname `metric` bleibt, aber Typ ist `measurement`)
- error        = reproduzierbarer Fehler
- decision     = nur aus bereits validierter Analyse ableitbar

### 6.2 Regelmatrix

| Eventtyp | Ohne reale Ausführung erlaubt? | Für Entscheidung tragfähig? |
| :--- | :--- | :--- |
| observation | ja | nein |
| run | nein | ja |
| measurement | nein | ja |
| error | nein | ja |
| decision | nein | ja, aber nur als Folge |

**Verdichtete Regel**

Observation informiert. Run legitimiert. Decision bindet.

### 6.3 Evidence-Shape

Das Repo hat bereits eine leichte Konvention. Diese würde ich erweitern, nicht sprengen.

Mindestfelder pro Zeile:

```json
{
  "event_type": "run",
  "timestamp": "2026-04-12T10:10:00Z",
  "iteration": 1,
  "metric": "execution",
  "value": "completed",
  "context": "benchmark: legacy-refactoring-v1",
  "notes": "Spec-first baseline run",
  "command": "python3 tools/run_benchmark.py --mode spec-first",
  "exit_code": 0,
  "artifact_ref": "results/artifacts/run-001.log"
}
```

Optional:
- duration_ms
- challenge_version
- mode
- trace_id

### 6.4 Provenienz und Verantwortlichkeit

Die Herkunft von Spuren muss klarer fassbar sein. Perspektivisch unterscheidet die Provenienz zwischen:
- `author`: Verfasser des Dokuments
- `executed_by`: Ausführende Entität (Mensch oder konkreter Agent)
- `reviewed_by`: Prüfende Instanz

⸻

## 7. Artefaktpflichten

### 7.1 Neue Ordnerstruktur für echte Runs

```
experiments/<name>/
  manifest.yml
  CONTEXT.md
  INITIAL.md
  method.md
  failure_modes.md
  results/
    evidence.jsonl
    result.md
    decision.yml           # nur wenn zulässig
    artifacts/
      run-001.log
      run-001-summary.json
      run-001-diff.patch
      run-001-test-output.txt
```

### 7.2 Was als Artefakt gilt
- Konsolenlog
- Testoutput
- Diff/Patch
- generierte Spec
- Fehlerprotokoll
- Metrik-Snapshot
- Screenshot/PDF eher nur ergänzend, nicht als Hauptbeweis

### 7.3 Was nicht als Beweis genügt
- result.md allein
- evidence.jsonl ohne Run-Artefakt
- eine plausible Beschreibung
- ein Agentenkommentar wie „wurde durchgeführt“

⸻

## 8. Validatoren und CI-Gates

### 8.1 Schema-Erweiterung für manifest.yml

Erweitere schemas/experiment.manifest.schema.json um:

```json
{
  "properties": {
    "experiment": {
      "properties": {
        "execution_status": {
          "type": "string",
          "enum": ["designed", "executed", "replicated", "reconstructed"]
        }
      }
    }
  }
}
```

**Regel**

execution_status wird required.

⸻

### 8.2 Validator: execution-proof-check

Neue Logik in scripts/docmeta/validate_schema.py oder besser eigener Check.

Pseudologik

```python
if manifest.experiment.execution_status in {"executed", "replicated"}:
    assert evidence.jsonl exists
    assert at least one event_type == "run"
    assert every run has artifact_ref (must be string)
    assert artifact path resolves strictly within experiment root
    assert referenced artifact files exist (is_file)

if decision.yml has adoption_assessment:
    assert manifest.experiment.execution_status in {"executed", "replicated"}
    assert evidence has run-events

if decision.yml has execution_assessment:
    # allowed for designed, reconstructed, executed, replicated
    pass
```

⸻

### 8.3 CI-Workflow-Gate

Neuer Check im Workflow:

```yaml
- name: Validate execution proof
  run: python3 scripts/docmeta/validate_execution_proof.py
```

⸻

## 9. Agentenpolitik härten

### 9.1 Verbotene Aktionen

In agent-policy.yaml ergänzen:

```yaml
forbidden_actions:
  - "write decision.yml for non-executed experiments"
  - "emit run-like evidence without corresponding artifacts"
  - "mark experiment as executed without execution proof"
```

### 9.2 Erforderliche Checks

```yaml
required_checks:
  - execution-proof-check
```

### 9.3 Capture-Schutz

Agenten dürfen weiterhin:
- Hypothesen entwerfen
- Designs formulieren
- Methoden schreiben

Sie dürfen aber nicht:
- Ausführung fingieren
- „echte“ Evidenz simulieren

⸻

## 10. Entscheidungslogik neu kalibrieren

### 10.1 Decision-Typen unterscheiden

Es gibt nicht die "eine" Entscheidung. `decision.yml` wird in drei semantische Typen aufgespalten:
- **`execution_assessment`**: Bewertet den Ausführungsstatus (z. B. "nicht ausgeführt", "nur rekonstruiert", "Proof fehlt").
- **`result_assessment`**: Bewertet die Ergebnisse auf Basis vorhandener Evidenz.
- **`adoption_assessment`**: Die harte Entscheidung zur Übernahme in kanonische Pfade.

### 10.2 Erlaubte Typen nach Status

- `execution_assessment` darf auch bei `designed` oder `reconstructed` existieren.
- `adoption_assessment` darf **nur** bei `executed` oder `replicated` existieren.

Nicht jede Entscheidung ist eine Adoption, und nicht jede Entscheidung setzt `executed` voraus. Aber Adoption setzt zwingend echte Durchführung voraus.

⸻

## 11. Migration des aktuellen Bestands

### 11.1 Bestandsmigration: Ehrliche Einstufung

Für den Altbestand gelten künftig drei ehrliche Wege:
- **`executed`**: Wenn echte Ausführungsspuren und Artefakte nachweisbar vorliegen.
- **`reconstructed`**: Wenn nur rekonstruierbare Altspuren oder Erfahrungswissen vorliegen. Dies bleibt erkenntnisfähig, ist aber nicht gleichrangig mit echter Ausführung. Rekonstruktion dokumentiert Vergangenheitsnähe, nicht Durchführungsbeweis. Was rekonstruiert ist, darf informativ sein, aber nicht proof-äquivalent. Es darf nie als Basis für ein `adoption_assessment` dienen.
- **`designed`**: Wenn das Experiment im aktuellen System nur als geplante oder nachträglich formulierte Struktur existiert.

Wichtiger Punkt:
Altbestand bekommt keinen Sonderbonus. Nostalgie ersetzt keinen Proof. Rekonstruktion wird explizit als solche ausgewiesen.

⸻

## 12. UX-Frage: Wie vermeiden wir, dass das System unbenutzbar wird?

Das ist der wichtigste Einwand.

Lösung: zweistufige Wahrheit

Stufe 1: Design-Wahrheit

Erlaubt:
- Hypothesen
- Methoden
- qualitative Erwartungen
- Rohideen

Stufe 2: Execution-Wahrheit

Erlaubt zusätzlich:
- Run-Claims
- Metrics
- Decisions
- Adoption

Merksatz

Nicht jede Idee braucht Proof.
Aber jede Durchführungsaussage braucht Proof.

⸻

## 13. Konkrete Inhalte für Repo-Dateien

### 13.1 Beispiel für manifest.yml

```yaml
schema_version: "0.1.0"

experiment:
  name: "spec-first-legacy-refactoring"
  hypothesis: "Spec-First reduziert Rework in Brownfield-Refactorings."
  status: testing
  execution_status: designed
  category: workflow
  created: "2026-04-12"
  updated: "2026-04-12"
  author: "heimgewebe"
  iteration: 1
  evidence_level: anecdotal

context:
  tools:
    - "LLM-Agent"
    - "Python"
  language: "Python"
  environment: "local benchmark run"

evidence:
  format: jsonl
  path: results/evidence.jsonl
```

### 13.2 Nach der echten Ausführung

```yaml
experiment:
  status: testing
  execution_status: executed
  evidence_level: experimental
```

⸻

### 13.3 Beispiel für results/evidence.jsonl

```json
{"event_type":"run","timestamp":"2026-04-12T10:00:00Z","iteration":1,"metric":"execution","value":"completed","context":"benchmark: legacy-refactoring-v1","notes":"Spec-first run completed","command":"python3 tools/run_legacy.py --mode spec-first","exit_code":0,"artifact_ref":"results/artifacts/run-001.log"}
{"event_type":"measurement","timestamp":"2026-04-12T10:02:13Z","iteration":1,"metric":"tests_passing","value":"18/24","context":"benchmark: legacy-refactoring-v1","notes":"First pass after generation","artifact_ref":"results/artifacts/run-001-test-output.txt"}
{"event_type":"error","timestamp":"2026-04-12T10:03:02Z","iteration":1,"metric":"regression","value":"payment_side_effect_changed","context":"benchmark: legacy-refactoring-v1","notes":"Observed changed behavior in refund path","artifact_ref":"results/artifacts/run-001.log"}
```

⸻

### 13.4 Beispiel für validate_execution_proof.py

```python
from pathlib import Path
import json
import yaml
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

def load_jsonl(path: Path):
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows

def main():
    errors = []

    for manifest_path in (REPO_ROOT / "experiments").glob("*/manifest.yml"):
        if manifest_path.parent.name.startswith("_"):
            continue

        data = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
        exp = data.get("experiment", {})
        execution_status = exp.get("execution_status")

        results_dir = manifest_path.parent / "results"
        decision_path = results_dir / "decision.yml"
        evidence_path = results_dir / "evidence.jsonl"

        if execution_status in {"executed", "replicated"}:
            if not evidence_path.exists():
                errors.append(f"{manifest_path}: execution_status={execution_status} but no evidence.jsonl")
                continue

            rows = load_jsonl(evidence_path)
            run_events = [r for r in rows if r.get("event_type") == "run"]
            if not run_events:
                errors.append(f"{manifest_path}: execution_status={execution_status} but no run event found")

            for r in run_events:
                artifact_ref = r.get("artifact_ref")
                if not artifact_ref:
                    errors.append(f"{manifest_path}: run event missing artifact_ref")
                    continue
                if not isinstance(artifact_ref, str):
                    errors.append(f"{manifest_path}: artifact_ref must be a string")
                    continue

                try:
                    artifact_path = (manifest_path.parent / artifact_ref).resolve()
                    # Prevent escape from experiment root
                    artifact_path.relative_to(manifest_path.parent.resolve())
                except ValueError:
                    errors.append(f"{manifest_path}: artifact_ref escapes experiment root: {artifact_ref}")
                    continue

                if not artifact_path.is_file():
                    errors.append(f"{manifest_path}: artifact_ref is not a valid file: {artifact_ref}")

        if decision_path.exists():
            decision_data = yaml.safe_load(decision_path.read_text(encoding="utf-8")) or {}

            # adoption_assessment needs executed/replicated
            if decision_data.get("type") == "adoption_assessment":
                if execution_status not in {"executed", "replicated"}:
                    errors.append(f"{manifest_path}: adoption_assessment requires executed or replicated status")

            # execution_assessment is fine for designed or reconstructed
            elif decision_data.get("type") == "execution_assessment":
                pass

    if errors:
        print("❌ Execution proof validation FAILED")
        for e in errors:
            print(" -", e)
        sys.exit(1)

    print("✅ Execution proof validation passed.")

if __name__ == "__main__":
    main()
```

⸻

### 13.5 Beispiel für results/decision.yml

Die Trennung der Decision-Typen erfordert minimale, explizite Dateien.

**Beispiel 1: execution_assessment**
```yaml
type: execution_assessment
verdict: not_executed
summary: "Kein echter Run-Proof vorhanden. Das Experiment ist nur designed."
```

**Beispiel 2: adoption_assessment**
```yaml
type: adoption_assessment
verdict: adopted
summary: "Auf Basis echter Run-Artefakte und Messwerte übernommen."
```

⸻

## 14. Einführungsplan in drei Phasen

### Phase A — Sofort
- execution_status ins Manifest
- neuer Validator
- decision.yml an execution_status binden
- Agent-Policy verschärfen

### Phase B — Bestandsbereinigung
- vorhandene Experimente neu klassifizieren
- falsche Abschlüsse entfernen
- observation vs run sauber trennen

### Phase C — Später
- echte CLI-Runner
- automatische Artefakterzeugung
- reproducible experiment runs
- Benchmarks als ausführbare Pipelines

⸻

## 15. Risiko-/Nutzenabschätzung

**Nutzen**
- echte epistemische Integrität
- weniger Simulationswissen
- höhere Reproduzierbarkeit
- bessere Grundlage für spätere Katalogeinträge

**Risiken**
- etwas mehr Prozesslast
- schwächere Frühphase, wenn man die Regeln falsch auf Capture ausweitet
- Versuchung, nur noch Messbares zu wertschätzen

**Kritischer Ausgleich**

Nur Durchführung hart binden, nicht Ideenbildung.
Das ist die ganze Kunst.

⸻

## 16. Resonanz- und Kontrastprüfung

**Deutung 1**

„Das ist zu viel Bürokratie für ein Vibe-Lab.“

Plausibel, wenn man Capture und Execution verwechselt.

**Deutung 2**

„Ohne harte Beweise bleibt das Repo eine Simulationsmaschine.“

Ebenfalls plausibel — und für deinen aktuellen Problemdruck näher an der Wahrheit.

**Synthese**

Nicht alles härten.
Nur die Stelle härten, an der aus Denken Wissen werden soll.

⸻

## 17. Was bewusst nicht zu tun ist
- Nicht sofort experiment-light einführen
- Nicht alle alten qualitative Beobachtungen löschen
- Nicht raw-vibes/ mit Beweispflichten überziehen
- Nicht die Repo-Semantik durch neue Top-Level-Strukturen aufblasen
- **Keine Diff-Lawinen:** Epistemische Härtung darf bestehende Artefakte nur dort verändern, wo es für semantische Korrektheit oder Validierung nötig ist. Stilistische oder formatierende Massenänderungen ohne Erkenntnisgewinn sind zu vermeiden (Minimalinvasivität).

⸻

## 18. Konkrete nächste PRs

**PR 1**

epistemic-hardening: bind execution claims to proof artifacts
- execution_status
- validator
- CI gate
- agent-policy rule

**PR 2**

reclassify existing experiments by execution status
- spec-first
- yolo-vs-spec-first

**PR 3**

first proof-bound benchmark execution
- echter Durchlauf auf legacy-refactoring-v1

⸻

## Essenz

**Hebel:** Durchführungsaussagen an Proof binden.
**Entscheidung:** Einführung eines harten execution_status + CI-Guards + Agentenverbote.
**Nächste Aktion:** zuerst den epistemischen Contract bauen, dann erst wieder Experimente „durchführen“.

**Unsicherheitsgrad:** 0.10
**Ursachen:** Die Lösung ist konzeptionell klar, aber wie streng du Altbestand rückwirkend behandeln willst, ist eine echte Governance-Entscheidung.

**Interpolationsgrad:** 0.14
**Hauptannahmen:** Du willst ein Erkenntnissystem und nicht bloß ein schön strukturiertes Diskussionsarchiv.

**Humorvoller Restbefund:**
Ein Repo, in dem Durchführung frei behauptet werden darf, ist wie ein Restaurant, in dem jeder „frisch gekocht“ auf die Karte schreiben darf, solange der Teller warm genug aussieht.
