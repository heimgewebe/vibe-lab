# AGENTS.md — Bindende Leseregeln für Agenten

> Dieses Dokument ist handgepflegt und kanonisch. Es wird nicht generiert.

## Lesereihenfolge

Agenten MÜSSEN Dokumente in dieser Reihenfolge lesen:

1. `repo.meta.yaml` — Maschinenlesbare Repo-Verfassung
2. `AGENTS.md` — Dieses Dokument
3. `agent-policy.yaml` — Operative Agentensteuerung
4. `README.md` — Projekteinstieg
5. `docs/index.md` — Navigation
6. Kanonische Pfade (`contracts/`, `schemas/`, `.vibe/`)
7. `docs/_generated/*` — Diagnose (nur lesen, nie editieren)

## Wahrheitshierarchie

| Ebene        | Quellen                                               | Charakter              |
| ------------ | ----------------------------------------------------- | ---------------------- |
| Wahrheit     | `repo.meta.yaml`, `AGENTS.md`, `agent-policy.yaml`   | Kanonisch, handgepflegt |
| Wahrheit     | `vision.md`, `repo-plan.md`, `contracts/*`, `schemas/*` | Kanonisch             |
| Operativ     | `README.md`, `CONTRIBUTING.md`, `.vibe/*`             | Handgepflegt           |
| Navigation   | `docs/index.md`                                       | Wegweiser              |
| Diagnose     | `docs/_generated/*`                                   | Maschinell, read-only  |

**Regel:** Bei Widersprüchen gilt die höhere Ebene.

## Generierte Artefakte

Die folgenden Pfade enthalten ausschließlich generierte Artefakte. Agenten dürfen sie lesen, aber **niemals manuell editieren**:

- `exports/`
- `.cursor/rules/`
- `docs/_generated/`

## Handgepflegte Steuerungsdokumente

Die folgenden Dokumente sind kanonisch und werden ausschließlich von Menschen gepflegt:

- `repo.meta.yaml`
- `AGENTS.md`
- `agent-policy.yaml`

## Verhaltensregeln

1. **Abbruch bei Konflikten:** Wenn ein generiertes Artefakt einer kanonischen Quelle widerspricht, bricht der Agent ab und meldet den Konflikt.
2. **Keine Eigeninterpretation:** Agenten ergänzen keine Konzepte, die nicht in den kanonischen Quellen angelegt sind.
3. **Transparenz:** Jede agentengesteuerte Änderung muss ihren Auslöser (`triggered_by`) dokumentieren.
4. **Zonenrespekt:** Die Dreiphasenlogik (Capture vs. Labor vs. Bibliothek) wird eingehalten. Capture-Artefakte (raw-vibes/) sind roh und unstrukturiert. Labor-Artefakte werden nicht ohne Promotion-Gate in die Bibliothek verschoben.
5. **Verbot ungerechtfertigter Status-Umdeutung:** Ein Experiment darf NUR dann auf `designed` gesetzt werden, wenn es belegt ist durch: (1) `decision.yml` mit `not_executed`, (2) explizite Textaussage im Experiment, oder (3) eindeutigen strukturellen Hinweis als reines Design-Artefakt. Fehlt der Run-Proof, bleibt der Status unberührt (epistemische Unklarheit aushalten, optional Hinweis notieren).
