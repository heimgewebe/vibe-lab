---
title: "Kontext: System-Map Artifact Coupling Isolation"
status: draft
canonicality: operative
relations:
  - type: informed_by
    target: "../2026-04-19_generated-artifact-contract-validation/results/cross-run-assessment.md"
---

# CONTEXT.md — System-Map Artifact Coupling Isolation

## Ausgangslage

Das abgeschlossene Experiment `2026-04-19_generated-artifact-contract-validation` hat über sechs Runs
(PR-58, PR-61, PR-62, PR-63, PR-64, PR-67) ein wiederkehrendes Strukturmuster dokumentiert:

Nach jedem Hinzufügen neuer Run-Artefakte unter `artifacts/run-*/` trat im PR-CI ein
blocking-CI-Fehler auf: stale `docs/_generated/system-map.md`. Behebung war in allen Runs
identisch: ein zusätzlicher canonical-Regenerationscommit (`make generate`).

Das Muster wurde in Run-003 bis Run-006 unabhängig von semantischer Friktion beobachtet.
Run-006 ist besonders relevant: pre-artifact-write war der Generator-Lauf sauber und deterministisch;
der stale-Fehler trat erst nach dem Schreiben neuer Run-Artefakte auf.

### Offene Leerstelle (aus cross-run-assessment.md §6, Punkt 4)

> "Bleibt Effekt bei reinem Doku-PR ohne neue Artefakte aus?"
> Status: Nicht vollständig abgehakt in diesem Datensatz; als Leerstelle markiert.

Diese Leerstelle ist der direkte Auslöser dieses Folgeexperiments.

### Warum das relevant ist

Das Vorgängerexperiment kann zwischen zwei Erklärungen nicht trennen:

**Erklärung A (Workflow):** Der Fehler entsteht durch Reihenfolge: Artefakte werden
geschrieben, dann wird der canonical state nicht sofort nachgezogen.
→ Lösung wäre reine Workflow-Disziplin: `make generate` immer nach Artifact-Write.

**Erklärung B (Architektur/Boundary):** Die Kopplung selbst ist problematisch: Canonical
diagnostics (`system-map.md` via `git ls-files`) reagieren auf run-interne Artefakte, die
nicht Teil der eigentlichen fachlichen Änderung sind.
→ Implikation: Das Problem verschwindet nicht durch Workflow-Disziplin allein; die
Contract-Grenze (was zählt als canonical-relevant?) wäre zu überdenken.

## Umgebung

- **Tools:** `make generate`, `make validate`, `git`, GitHub Actions
- **Generator:** `scripts/generate_system_map.py` (basiert auf `git ls-files`)
- **Sprache:** Mixed (Python-Skripte, Markdown-Artefakte)
- **Projekttyp:** Meta-Experiment-Repository (vibe-lab)
- **Modell(e):** Nicht relevant für dieses Diagnose-Experiment

## Relevante Vorarbeiten

- `experiments/2026-04-19_generated-artifact-contract-validation/` — Predecessor (6 Runs, stale-Muster etabliert)
- `experiments/2026-04-19_generated-artifact-contract-validation/results/cross-run-assessment.md` — Diagnoseoberfläche, Leerstelle dokumentiert
- `scripts/generate_system_map.py` — Zähllogik via `git ls-files` (relevant für Trigger-Analyse)

## Einschränkungen

- Dieses Experiment kann keine Aussage über andere Arten von canonical drift treffen;
  es fokussiert ausschließlich auf den `system-map.md`-Trigger.
- Der minimale Gegenlauf (kein Artifact-Write vor Validate) verändert das normale
  Arbeitsformat; Ergebnisse sind nicht direkt auf normale PR-Praxis übertragbar.
- Eine saubere Trennung A vs. B setzt einen tatsächlich durchgeführten Gegenlauf voraus.
  Solange dieser aussteht, bleibt die Ursachenfrage designed/not_measured.
