---
title: "Kontext: Agent Task Validity"
status: draft
canonicality: operative
---

# Kontext

Agenten erzeugen in PRs häufig Änderungen mit:

- unklarem Scope
- impliziten Annahmen
- zusätzlichen, nicht angefragten Modifikationen

Diese Muster führen zu:

- schwer reviewbaren PRs
- versteckten Seiteneffekten
- erhöhtem Rework

Das Experiment testet, ob ein explizites Task-Protokoll diese Probleme reduziert.

## Traceability

- **triggered_by:** User-Request zur Operationalisierung inkl. Diagnose-Gate und Stop-Regeln
- **policy:** repo.meta.yaml, AGENTS.md, agent-policy.yaml
- **action:** Neues Experimentdesign + Ausführungsinstruktion als reproduzierbares Paket angelegt
- **outcome (Iteration 1–3):** Run-Evidenz und Artefakte erhoben; Iteration 3 als echter Control-vs-Treatment-Lauf durchgeführt; verdict inconclusive wegen fehlendem Blind-Review.
- **outcome (Iteration 4 — Taskset):** tasks.iteration4.jsonl mit 8 Logic-Level-Tasks vorbereitet; Blind-Review-Template angelegt (review-notes-iteration4.md).
- **outcome (Iteration 4 — Ausführung):** NICHT BELEGT — Ausführungsclaims (run-005-control, run-006-treatment) geprüft: 0 von 8 Ziel-Datei-Änderungen im Repo vorhanden. Claims zurückgebaut. Siehe artifacts/iteration4-reconciliation.md.
- **outcome (Blind-Review):** AUSSTEHEND — verpflichtend per method.md Stop-Kriterium.
- **outcome (Replikation):** AUSSTEHEND — verpflichtend per method.md Stop-Kriterium.
- **Evidenztragender Stand:** Iteration 3 (run-003-control, run-004-treatment).
