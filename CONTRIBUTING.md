# Contributing to Vibe-Lab

Vibe-Lab ist ein lernendes System zur Sammlung, Erprobung und Weiterentwicklung von Vibe-Coding-Praktiken. **Nicht jede Idee muss sofort ein voll strukturiertes Experiment sein.** Das System hat drei Phasen mit aufsteigender Strenge.

## Drei Phasen

### Phase 1: Rohe Idee (`raw-vibes/`)

**Anforderung: keine.**

Lege eine Markdown-Datei in `raw-vibes/` an. Schreib auf, was dir auffällt — eine Beobachtung, eine Hypothese, ein Prompt-Fragment, eine Session-Notiz.

- Kein Schema, kein Frontmatter, keine Pflichtfelder
- Kein CI-Check, kein Review nötig
- Freie Struktur, freier Inhalt

**Wann weiter?** Wenn du glaubst, dass die Idee testbar ist und du sie strukturiert prüfen willst.

### Phase 2: Strukturiertes Experiment (`experiments/`)

**Anforderung: reproduzierbares Setup + Evidenz.**

1. Erstelle ein Issue mit dem Formular **🧪 Experiment Proposal**
2. Kopiere `experiments/_template/` in einen neuen Ordner
3. Fülle aus:
   - `manifest.yml` — Hypothese, Status, Metadaten
   - `method.md` — Vorgehen
   - `CONTEXT.md` — Ausgangszustand
   - `evidence.jsonl` — maschinenlesbare Beobachtungen

**Optional in dieser Phase:**
- `INITIAL.md` — initiale Prompt-/Setup-Situation
- `failure_modes.md` — bekannte Grenzen und Fehlannahmen

> `failure_modes.md`, `CONTEXT.md` und `INITIAL.md` sind erst bei Promotion verpflichtend. Für laufende Experimente sind sie empfohlen, aber nicht erzwungen.

**Schema-Validierung:** `make validate` prüft Manifest und Evidenz.

### Phase 3: Adoption / Bibliothek (`catalog/`, `prompts/adopted/`)

**Anforderung: volle Evidenz + harte Prüfung.**

Erst wenn ein Experiment belastbare Ergebnisse liefert, wird es zur Übernahme vorgeschlagen:

1. Erstelle einen PR mit dem Template **Promotion** (`promotion.md`)
2. **Alle** Pflichtartefakte müssen vollständig sein:
   - `CONTEXT.md` und `INITIAL.md` — vollständig ausgefüllt
   - `evidence.jsonl` — mindestens ein Eintrag
   - `decision.yml` — mit verdict (`adopted` / `rejected`)
   - `failure_modes.md` — ausgefüllt, keine Template-Platzhalter
3. Schema-Validierung muss bestehen (`make validate`)

**Keine Evidenz, keine Promotion.** Katalogeinträge ohne belastbare Experimentdaten werden nicht akzeptiert.

## Contribution Contract

Jeder Beitrag ordnet sich einem dieser Typen zu:

| Typ                  | Intake                          | Zielort                      | Anforderung                                                      |
| -------------------- | ------------------------------- | ---------------------------- | ---------------------------------------------------------------- |
| **Raw Vibe**         | Direkt in `raw-vibes/`          | `raw-vibes/`                 | Keine                                                            |
| **Innovation**       | Issue: `idea.yml`               | `experiments/`               | Hypothese formuliert, reproduzierbar                             |
| **Experiment**       | Issue: `experiment-proposal.yml`| `experiments/<name>/`        | Manifest und Methode initialisiert, `evidence.jsonl` vorhanden   |
| **Catalog Entry**    | PR: `promotion.md`             | `catalog/`                   | Experiment abgeschlossen, Evidenz belastbar, Schema valide       |
| **Combo**            | PR: `promotion.md`             | `catalog/combos/`            | Mindestens zwei Practices referenziert, eigene Evidenz vorhanden |
| **Prompt**           | PR: `promotion.md`             | `prompts/adopted/`           | Experiment-Rückverweis, menschenlesbar                           |
| **Decision Artifact**| PR / Review / Governance        | `decisions/`                 | Entsteht aus Prozess, nicht über eigenes Intake-Formular         |

> **Hinweis:** Decision Artifacts haben kein eigenes Issue-Formular. Sie entstehen typischerweise aus PR-Reviews, Governance-Diskussionen oder Prozess-Retrospektiven.

## Epistemischer Fluss

```
raw vibe → idea → testing → adopted / rejected
                              ↓
                          deprecated (bei Ablösung durch neue Evidenz)
```

Sonderstatus:
- **blocked** — pausiert aus externen Gründen (z.B. Tool-Bug, API-Release)
- **inconclusive** — kein belastbares Urteil; erzwingt explizite Entscheidung

## Qualitätsanforderungen (phasenabhängig)

| Anforderung | Raw Vibe | Experiment | Adoption |
|-------------|----------|------------|----------|
| Schema-Compliance | — | ✅ | ✅ |
| `manifest.yml` | — | ✅ | ✅ |
| `evidence.jsonl` | — | ✅ | ✅ |
| `CONTEXT.md` | — | ✅ | ✅ Pflicht |
| `INITIAL.md` | — | empfohlen | ✅ Pflicht |
| `failure_modes.md` | — | empfohlen | ✅ Pflicht |
| `decision.yml` | — | — | ✅ Pflicht |
| Promotion-PR | — | — | ✅ Pflicht |

## Lokale Validierung

```bash
make validate
```

Dieser Befehl führt den minimalen Guard-Stack aus (Schema- und Relations-Validierung). Er prüft `experiments/`, `catalog/` und `prompts/` — **nicht** `raw-vibes/`.

Generated diagnostics are classified by `.vibe/generated-artifacts.yml`. Canonical generated files and exports remain commit-required; derived diagnostics are optional and non-blocking. CI regenerates derived diagnostics for observability.

## Steuerungsdokumente

Die kanonischen Steuerungsdokumente des Repositories sind:
- `repo.meta.yaml` — Maschinenlesbare Repo-Verfassung
- `AGENTS.md` — Bindende Leseregeln für Agenten
- `agent-policy.yaml` — Agentensteuerung

Diese Dokumente sind handgepflegt und kanonisch. Sie werden nicht generiert.
