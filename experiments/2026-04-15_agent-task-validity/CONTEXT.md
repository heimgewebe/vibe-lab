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
- **outcome:** Run-Evidenz und Artefakte wurden erhoben (Iteration 1–4). Iteration 4 mit erhöhter Task-Komplexität. Blind-Review und Replikation ausstehend.
