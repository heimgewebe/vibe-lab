---
title: "Method — PR Agent Context Comparison Series"
status: designed
canonicality: operative
relations:
  - type: references
    target: "artifacts/run-template.md"
  - type: references
    target: "results/cross-run-assessment.md"
---

# Method — PR Agent Context Comparison Series

## Serienform

Die Serie besteht aus mehreren realen PR-Aufgaben. Jede Aufgabe wird genau einer
Condition zugeordnet. Die Conditions dürfen nicht während eines Runs vermischt
werden, sonst ist die Vergleichsfläche kontaminiert.

## Conditions

### A — Baseline: no structured handoff

Der Agent erhält nur die normale Nutzeranfrage und verfügbare PR-Informationen.
Keine Vibe-Lab-Runstruktur, kein Lenskit-Dump, keine explizite Evidence-Matrix.

Zweck: Arbeitsalltag ohne Laborstütze abbilden.

### B — Vibe-Lab handoff

Der Agent erhält eine strukturierte Aufgabe mit:

- Ziel und Nicht-Ziel.
- betroffenen Dateien oder PR-Kommentaren.
- Evidence-Gates.
- Stop-Kriterien.
- Pflicht zur Trennung von belegt, plausibel, spekulativ.
- erwarteten Artefakten.

Zweck: Prüfen, ob strukturierte Übergabe Review-Qualität erhöht und Rework senkt.

### C — Lenskit plus Vibe-Lab handoff

Der Agent erhält B plus einen Lenskit/repoLens-Kontext:

- Merge-Dump oder Agent Reading Pack.
- relevante Pfade oder Suchbegriffe.
- klare Regel: Derived navigation is not truth; claims must resolve to canonical
  source, code, logs, PR diff, or run artifacts.

Zweck: Prüfen, ob repo-spezifische Kontextlinsen Fehlannahmen und Locator-Lücken
senken.

### D — Minimal decision-first checklist

Der Agent erhält nur einen kleinen Entscheidungsfilter:

1. Belege den Ist-Zustand.
2. Nenne maximal drei Hypothesen.
3. Nenne zwei bis fünf Checks.
4. Definiere das Stop-Kriterium.
5. Erst danach Patch oder Review-Verdikt.

Zweck: Gegenprobe gegen Labordisziplin. Vielleicht ist ein Taschenmesser besser
als ein Operationssaal, wenn man nur einen Apfel schneiden will.

## Task-Auswahl

Zulässige Task-Klassen:

1. `review_comment_to_agent_instruction`: Aus einem PR-Review-Kommentar wird eine
   präzise Agent-Anweisung.
2. `review_comment_to_patch_plan`: Aus einem Review-Kommentar wird ein belegter
   Diagnose- und Patchplan.
3. `small_repo_fix`: Agent setzt einen kleinen Fix mit Tests um.
4. `diagnosis_only`: Agent prüft einen Fehler bis Target-Proof, ohne Patch.

Ausschlusskriterien:

- Aufgabe benötigt geheime Daten.
- Aufgabe ist nicht reproduzierbar dokumentierbar.
- Aufgabe verlangt neue Validatoren/Schemas als Teil des ersten Runs.
- Aufgabe ist so groß, dass Task-Difficulty die Condition vollständig dominiert.

## Required run artifacts

Jeder ausgeführte Run muss mindestens enthalten:

- `run.yml`
- `run_meta.json`
- `condition-input.md`
- `agent-output.md`
- `changed-files.txt` oder `no-changes.txt`
- `targeted-tests.txt` oder `diagnostic-checks.txt`
- `measurement.yml`
- `comparability.yml`
- `auditor-output.yml`
- `evidence-pack.yml`
- `timing.txt`

Bei Patch-Runs zusätzlich:

- `make-validate.txt` oder ein begründeter Ersatz.
- relevante Testausgaben.

## Messlogik

Primäre Messgrößen:

- unsupported_claim_count
- missing_locator_count
- scope_drift_count
- validation_gap_count
- review_friction_count
- rework_count
- false_block_count
- task_completion_time_observed

Zusätzliche Serienmetriken:

- evidence_quality_score: 0–3
- patch_acceptability: `not_applicable | rejected | needs_rework | acceptable`
- reviewer_correction_rounds: integer
- context_preparation_cost: observed minutes or `unknown`
- output_reuse_value: `none | partial | direct`

## Comparability rule

Ein Run ist nur vergleichbar, wenn folgende Felder dokumentiert sind:

- task_class
- condition
- source_pr_or_review_ref
- input_artifacts
- allowed_context
- disallowed_context
- output_requested
- validation_possible

Ein einzelner guter Run darf nur als Beobachtung zählen, nicht als Condition-
Effekt. Condition-Effekt-Claims benötigen mindestens drei vergleichbare Task-
Paare oder eine explizite Inconclusive-Entscheidung.

## Auswertungsregel

Vor `result_assessment` muss `results/cross-run-assessment.md` befüllt werden.
Bis dahin bleibt `results/decision.yml` bei `decision_type: execution_assessment`
und `verdict: not_executed` oder später `executed`.

## Stop-Kriterien

Die Serie wird gestoppt oder umgeplant, wenn:

- mehr als zwei Runs wegen unklarer Scope-Grenzen nicht vergleichbar sind;
- Condition C mehr Vorbereitung erzeugt, aber keine Locator- oder Claim-Qualität
  verbessert;
- Task-Auswahl zu heterogen ist;
- menschliche Reviewzeit nicht ausreichend erfasst werden kann.
