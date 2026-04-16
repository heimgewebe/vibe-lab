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
- **outcome (Iteration 4 — Primärrun):** Primärrun durchgeführt (run-005-control, run-006-treatment); Logic-Level-Tasks mit dokumentierten Drift-Temptations; artifact-Spur vorhanden.
- **outcome (Iteration 4 — Blind-Review):** AUSSTEHEND — verpflichtend per method.md Stop-Kriterium; PR darf nicht gemerged werden bis abgeschlossen.
- **outcome (Iteration 4 — Replikation):** AUSSTEHEND — verpflichtend per method.md Stop-Kriterium; PR darf nicht gemerged werden bis abgeschlossen.
- **Iteration-4-Abschluss:** NICHT ABGESCHLOSSEN — Primärrun ≠ vollständige Iteration 4.
