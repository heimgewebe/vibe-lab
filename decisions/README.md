---
title: "Decisions — Navigation"
status: active
canonicality: navigation
updated: "2026-05-18"
relations:
  - type: references
    target: ../docs/foundations/repo-plan.md
  - type: references
    target: benchmark/README.md
  - type: references
    target: export/README.md
  - type: references
    target: policy/README.md
---

# Decisions — Navigation

`decisions/` enthält **typisierte Meta-Entscheidungen** über das Repository selbst.
Hier wird keine inhaltliche Vibe-Coding-Praxis entschieden — das ist Aufgabe der
Promotion-Pipeline (`catalog/`, `prompts/adopted/`). Decisions betreffen
Repo-Governance, Prozess-Retrospektiven, System-Feature-Gates und Architektur-Weichen.

> **Navigationshinweis:** Diese Datei ist Wegweiser, kein kanonischer Inhalt.
> Bei Widersprüchen gelten die jeweiligen Decision-Artefakte und die
> übergeordneten Steuerdokumente (`repo.meta.yaml`, `AGENTS.md`, `agent-policy.yaml`).

## Typisierte Namespaces

| Namespace | Beschreibung | Status |
| --------- | ------------ | ------ |
| [system/](system/) | Operative Repo-Feature-Gates (`system_decision`-Schema); CI-blockierend | aktiv |
| [process/](process/) | Prozess-Retrospektiven, Remediation-Entscheide, Validator-Scope | aktiv |
| [benchmark/ →](benchmark/README.md) | Benchmark-Definitions- und Versionsentscheide | Stub-Namespace |
| [export/ →](export/README.md) | Export-Target-Entscheide, Sanitization, Format-Migration | Stub-Namespace |
| [policy/ →](policy/README.md) | Policy-flankierende Entscheide (`docs/policies/*.md`) | Stub-Namespace |

## Schema und Validierung

- **`decisions/system/`** wird von `scripts/docmeta/check_system_decisions.py` gegen
  `contracts/system_decision.schema.json` validiert (CI-blockierend via `make generate-metrics`).
- **`decisions/process/`** hat aktuell keinen eigenen Schema-Contract; Einträge werden
  manuell gepflegt und über Relations-Validierung überprüft.
- **Stub-Namespaces** haben noch keinen Pflicht-Contract. Beim ersten realen Eintrag
  wird entschieden, ob ein eigener Schema-Strang sinnvoll ist.

## Weiterführend

- [Repo-Plan](../docs/foundations/repo-plan.md) — Typisierte Decision Artifacts (Phase C)
- [AGENTS.md](../AGENTS.md) — Verhaltensregeln und Wahrheitshierarchie
- [agent-policy.yaml](../agent-policy.yaml) — Operative Agentensteuerung
