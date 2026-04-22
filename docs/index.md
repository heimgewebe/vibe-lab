---
title: "Dokumentation — Navigation"
status: active
canonicality: navigation
relations:
  - type: references
    target: blueprints/blueprint-agent-operability.md
  - type: references
    target: blueprints/blueprint-agent-operability-phase-1c.md
  - type: references
    target: policies/interpretation-budget.md
  - type: references
    target: playbooks/reconciliation.md
  - type: references
    target: playbooks/build-reliable-prompt.md
  - type: references
    target: ../catalog/combos/spec-first-constraint-control.md
  - type: references
    target: ../catalog/combos/spec-first-anti-pattern-awareness.md
  - type: references
    target: ../catalog/workflows/spec-first-api-generation.md
  - type: references
    target: ../catalog/workflows/causal-control-study.md
  - type: references
    target: ../catalog/styles/constraint-first.md
  - type: references
    target: ../catalog/styles/structured-specification.md
  - type: references
    target: ../instruction-blocks/spec-first.md
  - type: references
    target: ../instruction-blocks/constraint-before-code.md
  - type: references
    target: ../instruction-blocks/validate-against-spec.md
  - type: references
    target: ../instruction-blocks/no-vague-prompts.md
  - type: references
    target: ../instruction-blocks/edge-case-enumeration.md
  - type: references
    target: reference/agent-operability-fixture-matrix.md
---

# Vibe-Lab Dokumentation

> **Hinweis:** Diese Datei ist ausschließlich Navigation — kein kanonischer Inhalt. Bei Widersprüchen gelten die referenzierten Quelldokumente.

## Einstieg

| Dokument                              | Zweck                                    |
| ------------------------------------- | ---------------------------------------- |
| [README](../README.md)               | Projekteinstieg und Schnellstart         |
| [CONTRIBUTING](../CONTRIBUTING.md)    | Contribution Contract und Beitragstypen  |
| [Masterplan](masterplan.md)           | Inhaltlicher Anker und Zielbild          |


## Grundlagen

| Dokument                                      | Zweck                               |
| --------------------------------------------- | ----------------------------------- |
| [Vision](foundations/vision.md)               | Systemvision und Layer-Architektur  |
| [Repo-Plan](foundations/repo-plan.md)         | Architektur- und Umsetzungsplan     |

## Steuerungsdokumente

| Dokument                                      | Zweck                               |
| --------------------------------------------- | ----------------------------------- |
| [repo.meta.yaml](../repo.meta.yaml)          | Maschinenlesbare Repo-Verfassung    |
| [AGENTS.md](../AGENTS.md)                    | Bindende Leseregeln für Agenten     |
| [agent-policy.yaml](../agent-policy.yaml)    | Operative Agentensteuerung          |

## Epistemische Dokumentpfade

| Ordner                    | Inhalt                                      |
| ------------------------- | ------------------------------------------- |
| [raw-vibes/](../raw-vibes/) | Rohe Ideen und Beobachtungen                |
| [concepts/](concepts/)    | Unvalidierte Begriffe und Denkmodelle       |
| [experiments/](experiments/) | Dokumentationsebene für Versuchsdesign   |
| [evaluations/](evaluations/) | Auswertungen und Bewertungen             |
| [syntheses/](syntheses/)  | Verdichtete Erkenntnisse                    |
| [rules/](rules/)          | Operationalisierte Regeln                   |
| [blueprints/](blueprints/) | Überführung in Praxis                      |
| [policies/](policies/)    | Richtlinien und Policy-Dokumente            |
| [reference/](reference/)  | Nachschlagewerke und Referenzmaterial       |
| [playbooks/](playbooks/)  | Triage-Runbooks und operative Anleitungen   |
| [onboarding/](onboarding/) | Einstiegsdokumentation                     |

## Policies (direkte Referenzen)

| Dokument | Zweck |
| -------- | ----- |
| [policies/privacy-and-ethics.md](policies/privacy-and-ethics.md) | Datenschutz- und Ethikvorgaben |
| [policies/interpretation-budget.md](policies/interpretation-budget.md) | Guard gegen Overclaiming bei Promotion |

## Diagnose (Generiert)

> Diese Dateien werden maschinell erzeugt und dürfen nicht manuell editiert werden.

| Datei                                           | Klasse | CI-Verhalten | Inhalt |
| ----------------------------------------------- | ------ | ------------ | ------ |
| [_generated/doc-index.md](_generated/doc-index.md)     | canonical | blocking | Dokumenten-Index |
| [_generated/system-map.md](_generated/system-map.md)   | canonical | blocking | Systemübersicht |
| [_generated/backlinks.md](_generated/backlinks.md)     | derived | non-blocking | Rückverlinkungen |
| [_generated/orphans.md](_generated/orphans.md)         | derived | non-blocking | Verwaiste Dokumente |
| `_generated/epistemic-state.md` (CI-Artifact)          | ephemeral | artifact-only | Abgeleiteter Zustands-Snapshot |

## Exports (Generiert)

> Abgeleitete, toolspezifische Repräsentationen aus `instruction-blocks/`. Exports sind keine eigenständige Wahrheitsquelle — sie leiten sich vollständig aus den Quelldateien ab und werden deterministisch regeneriert. Jeder Export enthält eine quellgebundene Herkunftsmarkierung (`source-hash`), die eine eindeutige Zuordnung zur Quelldatei sicherstellt.

| Zielordner | Quelle | Regeneration |
| ---------- | ------ | ------------ |
| [`exports/copilot/`](../exports/copilot/) | `instruction-blocks/*.md` | `make generate-exports` |
| [`exports/cursor/`](../exports/cursor/) | `instruction-blocks/*.md` | `make generate-exports` |

Warum Exporte abgeleitete Artefakte sind: Sie enthalten keinen eigenständigen Inhalt, sondern transformieren validierte Instruction-Blocks in eine konsumierbare Form für externe Tools. Die Quelldateien in `instruction-blocks/` bleiben die einzige Wahrheitsquelle.

## Schemas und Verträge

| Datei                                                      | Zweck                               |
| ---------------------------------------------------------- | ----------------------------------- |
| [contracts/docmeta.schema.json](../contracts/docmeta.schema.json)   | Frontmatter-Schema         |
| [schemas/experiment.manifest.schema.json](../schemas/experiment.manifest.schema.json) | Experiment-Manifest  |
| [schemas/catalog.entry.schema.json](../schemas/catalog.entry.schema.json) | Katalogeintrag         |
| [schemas/combo.schema.json](../schemas/combo.schema.json) | Combo-Eintrag                       |


## Laufende Versuche
- [Experimenten-Labor](../experiments/README.md)

## Blueprints

- [Minimaler Agent-Operability-Kern](blueprints/blueprint-agent-operability.md)
- [Phase 1c: Systemverankerung des Agent-Operability-Kerns](blueprints/blueprint-agent-operability-phase-1c.md)

## Konzepte (latent)

- [Execution-Bound Epistemics](concepts/execution-bound-epistemics.md)
- [Iteration, Execution Scope und Reconciliation](concepts/experiment-ontology.md)

## Playbooks

- [Reconciliation](playbooks/reconciliation.md)
- [Build a Reliable Prompt](playbooks/build-reliable-prompt.md)

## Bibliothek

### Catalog

| Zone | Inhalt |
| ---- | ------ |
| [catalog/techniques/](../catalog/techniques/) | Validierte Prompting-Techniken |
| [catalog/anti-patterns/](../catalog/anti-patterns/) | Dokumentierte Anti-Pattern |
| [catalog/combos/](../catalog/combos/) | Kuratierte Technique-Kombinationen |
| [catalog/workflows/](../catalog/workflows/) | Operative Workflows |
| [catalog/styles/](../catalog/styles/) | Prompting-Stile |
| [prompts/adopted/](../prompts/adopted/) | Adoptierte Prompt-Templates |

### Instruction Blocks

Portable Denkbausteine für Prompts und Workflows:

- [Spec-First](../instruction-blocks/spec-first.md)
- [Constraint-Before-Code](../instruction-blocks/constraint-before-code.md)
- [Validate-Against-Spec](../instruction-blocks/validate-against-spec.md)
- [No-Vague-Prompts](../instruction-blocks/no-vague-prompts.md)
- [Edge-Case-Enumeration](../instruction-blocks/edge-case-enumeration.md)

## Referenz

- [Manifest-Schema-Semantik](reference/manifest-schema.md)
- [Agent Operability — Fixture-Matrix (v0.1)](reference/agent-operability-fixture-matrix.md)
