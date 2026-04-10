# Vibe-Lab

**Exekutierbarer Erkenntnisraum für Vibe-Coding-Praktiken.**

Vibe-Lab ist kein passives Ideenarchiv, sondern ein lernendes System zur Sammlung, Erprobung und Weiterentwicklung von Vibe-Coding-Praktiken. Das System verbessert nicht nur Coding, sondern sich selbst.

## Was ist Vibe-Lab?

Das Repository realisiert die Pipeline **Sammlung → Erprobung → Validierung → Kreation**:

- **Sammlung (roh):** Ideen und Hypothesen werden über typisierte Issue-Formulare eingebracht.
- **Erprobung (getestet):** Strukturierte Experimente mit reproduzierbarem Setup prüfen Hypothesen.
- **Validierung (bewährt):** Nur evidenzbasierte Praktiken werden in den Katalog aufgenommen.
- **Kreation (systemisch erweitert):** Validierte Praktiken fließen als Instruction Blocks und Exports ins Ökosystem zurück.

## Zweizonenlogik

| Zone         | Ort                  | Charakter                        |
| ------------ | -------------------- | -------------------------------- |
| **Labor**    | `experiments/`       | Freie Exploration, hohe Varianz  |
| **Bibliothek** | `catalog/`, `prompts/`, `benchmarks/` | Validiertes Wissen, harte Checks |

## Schnellstart

### Idee einreichen
Erstelle ein Issue mit dem Formular **Idea** → [Neues Issue](.github/ISSUE_TEMPLATE/idea.yml)

### Experiment starten
Erstelle ein Issue mit dem Formular **Experiment Proposal** → kopiere `experiments/_template/` in einen neuen Ordner.

### Ergebnis zur Übernahme vorschlagen
Erstelle einen PR mit dem Template **Promotion** (`promotion.md`).

### Lokal validieren
```bash
make validate
```

## Contribution Contract

Jeder Beitrag muss einem der folgenden Typen entsprechen: **Innovation**, **Experiment**, **Catalog Entry**, **Combo**, **Prompt** oder **Decision Artifact**. Details: [CONTRIBUTING.md](CONTRIBUTING.md).

## Steuerungsdokumente

| Dokument              | Zweck                               | Status          |
| --------------------- | ----------------------------------- | --------------- |
| `repo.meta.yaml`      | Maschinenlesbare Repo-Verfassung    | Kanonisch       |
| `AGENTS.md`           | Bindende Leseregeln für Agenten     | Kanonisch       |
| `agent-policy.yaml`   | Operative Agentensteuerung          | Kanonisch       |
| `vision.md`           | Systemvision                        | Kanonisch       |
| `repo-plan.md`        | Architektur- und Umsetzungsplan     | Kanonisch       |

## Wahrheitshierarchie

1. **Kanonische Quellen** — `repo.meta.yaml`, `AGENTS.md`, `agent-policy.yaml`, `vision.md`, `repo-plan.md`, `contracts/*`, `schemas/*`
2. **Operative Dokumente** — `README.md`, `CONTRIBUTING.md`, `.vibe/*`
3. **Navigation** — `docs/index.md` (Wegweiser, nicht Wahrheit)
4. **Diagnose** — `docs/_generated/*` (maschinell, read-only)

## Projektstruktur

```
vibe-lab/
  README.md, CONTRIBUTING.md      # Operatives Einstiegssystem
  repo.meta.yaml                  # Maschinenlesbare Repo-Verfassung
  AGENTS.md, agent-policy.yaml    # Agentensteuerung
  .vibe/                          # Repo-operative Verträge
  contracts/                      # Kanonische/policy-nahe Schemas
  schemas/                        # Pipeline-Validierungs-Schemas
  experiments/                    # Labor: Materialisierte Testläufe
  catalog/                        # Bibliothek: Validiertes Wissen
  prompts/                        # Bibliothek: Menschenlesbare Artefakte
  benchmarks/                     # Bibliothek: Vergleichsaufgaben
  decisions/                      # Meta-Entscheidungen
  docs/                           # Epistemische Dokumentpfade
  scripts/                        # Guard-/Generator-Stack
  tools/                          # CLI / Automatisierung
```

## Weiterführend

- [Vision](vision.md)
- [Repo-Plan](repo-plan.md)
- [Contributing](CONTRIBUTING.md)
- [Dokumentation](docs/index.md)