# Contributing to Vibe-Lab

Vibe-Lab ist ein lernendes System zur Sammlung, Erprobung und Weiterentwicklung von Vibe-Coding-Praktiken. Jeder Beitrag durchläuft einen strukturierten Erkenntniskreislauf — von der Idee über das Experiment bis zur validierten Praxis.

## Contribution Contract

Jeder Beitrag muss einem der folgenden Typen zugeordnet sein:

| Typ                  | Intake                          | Zielort                      | Anforderung                                                      |
| -------------------- | ------------------------------- | ---------------------------- | ---------------------------------------------------------------- |
| **Innovation**       | Issue: `idea.yml`               | `experiments/`               | Hypothese formuliert, reproduzierbar                             |
| **Experiment**       | Issue: `experiment-proposal.yml`| `experiments/<name>/`        | Golden Skeleton vollständig, `evidence.jsonl` vorhanden          |
| **Catalog Entry**    | PR: `promotion.md`             | `catalog/`                   | Experiment abgeschlossen, Evidenz belastbar, Schema valide       |
| **Combo**            | PR: `promotion.md`             | `catalog/combos/`            | Mindestens zwei Practices referenziert, eigene Evidenz vorhanden |
| **Prompt**           | PR: `promotion.md`             | `prompts/adopted/`           | Experiment-Rückverweis, menschenlesbar                           |
| **Decision Artifact**| PR / Review / Governance        | `decisions/`                 | Entsteht aus Prozess, nicht über eigenes Intake-Formular         |

> **Hinweis:** Decision Artifacts haben kein eigenes Issue-Formular. Sie entstehen typischerweise aus PR-Reviews, Governance-Diskussionen oder Prozess-Retrospektiven.

## Epistemischer Fluss

```
idea → testing → adopted / rejected
                  ↓
              deprecated (bei Ablösung durch neue Evidenz)
```

Sonderstatus:
- **blocked** — pausiert aus externen Gründen (z.B. Tool-Bug, API-Release)
- **inconclusive** — kein belastbares Urteil; erzwingt explizite Entscheidung

## Wie du beitragen kannst

### 1. Idee einreichen
Nutze das Issue-Formular **Idea** (`idea.yml`), um eine neue Hypothese oder Beobachtung einzubringen.

### 2. Experiment vorschlagen
Nutze das Issue-Formular **Experiment Proposal** (`experiment-proposal.yml`), um ein strukturiertes Experiment zu beantragen. Du erhältst ein Golden Skeleton unter `experiments/_template/`.

### 3. Ergebnis zur Übernahme vorschlagen
Erstelle einen PR mit dem Template **Promotion** (`promotion.md`). Voraussetzung:
- Vollständiges Experiment mit `CONTEXT.md`, `INITIAL.md`, `manifest.yml`, `method.md`, `evidence.jsonl` und `decision.yml`
- Schema-Validierung muss bestehen (`make validate`)

## Qualitätsanforderungen

- **Keine Evidenz, keine Promotion.** Katalogeinträge ohne belastbare Experimentdaten werden nicht akzeptiert.
- **Reproduzierbarkeit.** `CONTEXT.md` und `INITIAL.md` müssen den Experimentkontext vollständig dokumentieren.
- **Schema-Compliance.** Alle Artefakte müssen gegen die Schemas in `schemas/` und `contracts/` validieren.
- **Keine manuellen Edits** an generierten Artefakten (`exports/`, `.cursor/rules/`, `docs/_generated/`).

## Lokale Validierung

```bash
make validate
```

Dieser Befehl führt den minimalen Guard-Stack aus (Schema- und Relations-Validierung).

## Steuerungsdokumente

Die kanonischen Steuerungsdokumente des Repositories sind:
- `repo.meta.yaml` — Maschinenlesbare Repo-Verfassung
- `AGENTS.md` — Bindende Leseregeln für Agenten
- `agent-policy.yaml` — Agentensteuerung

Diese Dokumente sind handgepflegt und kanonisch. Sie werden nicht generiert.

## Wahrheitshierarchie

1. **Kanonische Steuerungsdokumente** (`repo.meta.yaml`, `AGENTS.md`, `agent-policy.yaml`) — Wahrheit
2. **Operative Dokumente** (`README.md`, `CONTRIBUTING.md`, `.vibe/`) — Wahrheit
3. **Navigation** (`docs/index.md`) — Wegweiser, nicht Wahrheit
4. **Diagnose** (`docs/_generated/`) — Maschinell erzeugt, nicht manuell editierbar
