# Vibe-Lab

**Exekutierbarer Erkenntnisraum für Vibe-Coding-Praktiken.**

Vibe-Lab sammelt, erprobt und validiert Vibe-Coding-Praktiken. Nicht alles muss sofort ein schweres epistemisches Objekt sein — die meisten Ideen starten roh und werden erst bei Bedarf strukturiert.

## Schnellstart

### 💡 Rohe Idee festhalten (sofort, ohne Setup)

Lege eine Markdown-Datei in `raw-vibes/` an:

```bash
echo "# Meine Beobachtung\n\nChain-of-Thought scheint bei Refactoring besser zu funktionieren als..." \
  > raw-vibes/chain-of-thought-refactoring.md
```

Kein Schema, kein Frontmatter, keine CI-Prüfung. Einfach festhalten.

### 🧪 Strukturiertes Experiment starten

Wenn eine Idee reif genug zum Testen ist:

1. Erstelle ein Issue mit dem Formular **🧪 Experiment Proposal**
2. Kopiere `experiments/_template/` in einen neuen Ordner
3. Fülle `manifest.yml`, `method.md` und `CONTEXT.md` aus
4. Sammle Evidenz in `evidence.jsonl`

### 📚 Ergebnis in den Katalog übernehmen

Erst wenn ein Experiment belastbare Evidenz liefert:

1. Erstelle einen Pull Request mit dem Template **Promotion**
2. Alle Pflichtartefakte müssen vollständig sein (`make validate`)
3. Review + Merge = adoptierte Praxis

### Lokal validieren

```bash
make validate
```

## Drei Phasen, aufsteigende Strenge

| Phase | Ort | Anforderung | Charakter |
|-------|-----|-------------|-----------|
| **Roh** | `raw-vibes/` | Keine | Spontan, frei, unstrukturiert |
| **Experiment** | `experiments/` | Manifest, Methode, Evidenz | Strukturiert, reproduzierbar |
| **Bibliothek** | `catalog/`, `prompts/adopted/` | Volle Validierung, Promotion-Gate | Hart geprüft, evidenzbasiert |

**Prinzip:** Leicht am Eingang, hart am Ausgang.

## Projektstruktur

```
vibe-lab/
  raw-vibes/                      # Rohe Ideen, Notizen, Fragmente
  experiments/                    # Labor: Strukturierte Testläufe
  catalog/                        # Bibliothek: Validiertes Wissen
  prompts/                        # Bibliothek: Menschenlesbare Artefakte
  benchmarks/                     # Bibliothek: Vergleichsaufgaben
  decisions/                      # Meta-Entscheidungen
  docs/                           # Epistemische Dokumentpfade
  contracts/                      # Kanonische/policy-nahe Schemas
  schemas/                        # Pipeline-Validierungs-Schemas
  scripts/                        # Guard-/Generator-Stack
  tools/                          # CLI / Automatisierung
  .vibe/                          # Repo-operative Verträge
```

## Steuerung & Governance

<details>
<summary>Steuerungsdokumente und Wahrheitshierarchie (für Fortgeschrittene)</summary>

| Dokument              | Zweck                               | Status          |
| --------------------- | ----------------------------------- | --------------- |
| `repo.meta.yaml`      | Maschinenlesbare Repo-Verfassung    | Kanonisch       |
| `AGENTS.md`           | Bindende Leseregeln für Agenten     | Kanonisch       |
| `agent-policy.yaml`   | Operative Agentensteuerung          | Kanonisch       |
| `docs/foundations/vision.md`          | Systemvision                        | Grundlagendokument / Zielbild           |
| `docs/foundations/repo-plan.md`       | Architektur- und Umsetzungsplan     | Grundlagendokument / Umsetzungsrahmen     |

**Wahrheitshierarchie:**

1. **Kanonische Steuerungsquellen** — `repo.meta.yaml`, `AGENTS.md`, `agent-policy.yaml`, `contracts/*`, `schemas/*`
2. **Grundlagenquellen** — `docs/foundations/vision.md`, `docs/foundations/repo-plan.md`
3. **Operative Dokumente** — `README.md`, `CONTRIBUTING.md`, `.vibe/*`
4. **Navigation** — `docs/index.md` (Wegweiser, nicht Wahrheit)
5. **Diagnose** — `docs/_generated/*` (maschinell, read-only)

</details>

## Weiterführend

- [Contributing](CONTRIBUTING.md) — Phasenmodell, Beitragstypen, Qualitätsanforderungen
- [Vision](docs/foundations/vision.md)
- [Repo-Plan](docs/foundations/repo-plan.md)
- [Dokumentation](docs/index.md)
