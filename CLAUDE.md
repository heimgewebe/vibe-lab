# CLAUDE.md — Anker für Claude Code

> Dieses Dokument ist ein **Anker für Claude-Code-Agenten**. Es ist kein
> kanonischer Inhalt. Die kanonische Quelle ist [`AGENTS.md`](AGENTS.md).
> Bei Widersprüchen zwischen dieser Datei und kanonischen Quellen gilt
> immer die kanonische Quelle.

## Bevor du irgendetwas tust

**Lies zuerst die kanonischen Steuerungsdokumente in dieser Reihenfolge:**

1. [`repo.meta.yaml`](repo.meta.yaml) — Repo-Verfassung
2. [`AGENTS.md`](AGENTS.md) — Bindende Leseregeln (Pflicht)
3. [`agent-policy.yaml`](agent-policy.yaml) — Operative Agentensteuerung
4. [`docs/roadmap.md`](docs/roadmap.md) — Strategischer Kontext
5. [`README.md`](README.md) — Projekteinstieg
6. [`docs/index.md`](docs/index.md) — Navigation
7. `contracts/`, `schemas/`, `.vibe/` — Verträge und Restriktionen

Bei Widersprüchen gewinnt die höhere Ebene
(canonical > foundational > operative > navigation > diagnosis).

## Die fünf Verbote (Kurzform — Quelle: `AGENTS.md` und `.vibe/constraints.yml`)

1. **Nicht** `repo.meta.yaml`, `AGENTS.md`, `agent-policy.yaml` oder
   `.vibe/pr-scope-policy.yml` editieren — diese sind kanonisch und
   ausschließlich handgepflegt.
2. **Nicht** `docs/_generated/*`, `exports/*` oder `.cursor/rules/*` manuell
   editieren — diese sind generiert und werden über Generatoren
   regeneriert (`make generate`).
3. **Nicht** Status bestehender Experimente ohne belegte Grundlage ändern
   (siehe AGENTS.md → „Verbot unbelegter Status-Umdeutung").
4. **Nicht** Labor-Artefakte ohne Promotion-Gate in die Bibliothek
   (`catalog/`, `prompts/adopted/`, `benchmarks/`) verschieben.
5. **Nicht** Konzepte oder Felder erfinden, die nicht in den kanonischen
   Quellen oder Schemas angelegt sind.

## Schneller Eigen-Check

Vor jedem Commit:

```bash
make agent-check    # 2-Sekunden-Guard: kanonische und generierte Pfade
make validate       # vollständige Validierung (~150 s)
```

Bei Verstoß: **abbrechen** und Konflikt melden (`triggered_by`, `policy`,
`action`, `outcome` — siehe `agent-policy.yaml:traceability`).

## Zonenrespekt

| Zone | Pfade | Freiheit |
|------|-------|----------|
| Capture | `raw-vibes/*` | sehr hoch — keine Pflichten |
| Labor | `experiments/*` | hoch — Manifest und Methode nötig |
| Bibliothek | `catalog/*`, `prompts/*`, `benchmarks/*`, `instruction-blocks/*` | niedrig — Promotion-Gate erzwungen |

## Wenn du nicht sicher bist

- **Stopp und melden** ist immer besser als raten.
- Bei Konflikten zwischen generiertem Artefakt und kanonischer Quelle:
  Abbruch und Meldung (siehe `agent-policy.yaml:conflict_resolution`).
- Epistemische Unklarheit ist explizit auszuhalten — nicht überspielen.

## Weiterführend

- Vollständige Regeln: [`AGENTS.md`](AGENTS.md)
- Compliance-Policy: [`docs/policies/agent-compliance.md`](docs/policies/agent-compliance.md)
- Operative Restriktionen: [`.vibe/constraints.yml`](.vibe/constraints.yml)
- Qualitäts-Gates: [`.vibe/quality-gates.yml`](.vibe/quality-gates.yml)
