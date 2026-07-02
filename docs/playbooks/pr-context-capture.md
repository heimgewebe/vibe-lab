---
title: "Playbook: PR Context Capture"
status: active
canonicality: operative
schema_version: "0.1.0"
created: "2026-07-02"
updated: "2026-07-02"
author: "heimgewebe"
relations:
  - type: references
    target: operator-lab-loop.md
  - type: references
    target: pr-run-evidence-pack.md
  - type: references
    target: ../../experiments/2026-06-10_pr-agent-context-comparison-series/pilot-v1.yml
  - type: references
    target: ../../tools/vibe-cli/pr_context_capture.py
  - type: references
    target: ../../tools/vibe-cli/test_pr_context_capture.py
tags:
  - playbook
  - pr
  - evidence
  - operator
---

# Playbook: PR Context Capture

> Zweck: `tools/vibe-cli/pr_context_capture.py` erfasst kleine, repo-lokale Timing- und Review-Spuren fuer den frozen PR-context pilot. Es ist ein Capture-Helfer, kein Freigabeautomat.

## 1. Wann nutzen

Nutze den Capture-Helfer nur fuer Runs, die wirklich in den PR-context pilot gehoeren:

- ein Pair aus `experiments/2026-06-10_pr-agent-context-comparison-series/pilot-v1.yml` wird ausgefuehrt;
- ein konkreter Task-Slot ist gebunden;
- Rollen sind gebunden;
- der Pilot-Validator erlaubt Ausfuehrung.

Wenn der Pilot blockiert ist, muss `prepare` stoppen und den Grund melden. Ein blockierter Pilot darf keine halb angelegte Run-Directory erzeugen.

## 2. Minimaler Ablauf

Beispiel:

```bash
python3 tools/vibe-cli/pr_context_capture.py prepare \
  --run-id run-example \
  --pair-id pair-01 \
  --slot 1 \
  --executor operator:example \
  --base-commit abcdef0

python3 tools/vibe-cli/pr_context_capture.py start --run-id run-example --phase preparation
python3 tools/vibe-cli/pr_context_capture.py stop --run-id run-example
```

Phasen sind fest:

```text
preparation
execution
validation
review
rework
```

Jede Phase muss gestartet und gestoppt werden, bevor `finalize` erfolgreich sein darf.

## 3. Pflichtartefakte vor Finalize

Vor `finalize` muessen im Run-Verzeichnis mindestens diese Dateien vorhanden sein:

```text
agent-output.md
review-events.yml
```

Zusaetzlich braucht der Run Validierungs- und Scope-Evidence:

```text
targeted-tests.txt oder diagnostic-checks.txt
changed-files.txt oder no-changes.txt
```

Fehlt eines davon, bleibt der Run unfinalisiert. Das ist gewollt: fehlende Evidence ist ein sichtbarer Mangel, kein stiller Erfolg.

## 4. Review-Evidence

Review-Evidence wird ueber `review` geschrieben:

```bash
python3 tools/vibe-cli/pr_context_capture.py review \
  --run-id run-example \
  --pr-ref PR-123 \
  --rounds 2 \
  --rework-commit abcdef1
```

`rounds` zaehlt beobachtete Review-Friction. `rework-commit` ist nur fuer konkrete Rework-Commits gedacht. Mehrfachangabe ist erlaubt; doppelte Commits sind ungueltig.

## 5. Was `prepare` garantiert

`prepare` macht vor dem Schreiben einen Validator-Preflight:

- Pilot-YAML muss strukturell valide sein.
- `execution_allowed` muss wahr sein.
- Bedingungsdatei muss innerhalb des Experiments liegen.
- Bedingungs-Hash muss zu den eingefrorenen Bytes passen.
- Run-ID darf noch nicht existieren.

Bei blockiertem Pilot meldet der Fehler die abgeleiteten Blocker, zum Beispiel:

```text
pilot execution is blocked: tasks_not_bound, role_bindings_missing
```

## 6. Was nicht behauptet wird

Ein finalisierter Capture-Run belegt nur, dass die angegebenen Phasen und Evidence-Dateien repo-lokal erfasst wurden.

Er belegt nicht:

- dass eine Condition besser ist;
- dass ein Agent generell zuverlaessig ist;
- dass der PR korrekt ist;
- dass ein Review unabhaengig genug war;
- dass die Capture-Metriken bereits Outcome-Nutzen beweisen.

## 7. Validierung

Vor einem PR mit Capture-Aenderungen mindestens ausfuehren:

```bash
make validate-pr-context-pilot-tests
make validate-pr-context-pilot
```

Bei Operator-Lab-Bezug zusaetzlich:

```bash
make validate-operator-lab-run-cards-tests
make validate-operator-lab-run-cards
```

## 8. Ablage

Standard-Workdir:

```text
.tmp/pr-context-runs/<run-id>/
```

`.tmp` ist bewusst nicht finaler Evidence-Ort. Fuer dauerhafte PR-Claims gehoert die verdichtete Evidence in ein PR-Evidence-Pack oder eine Operator-Lab-Run-Card.
