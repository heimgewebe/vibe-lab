# GEMINI.md — Anker für Gemini Code Assist

> Dieses Dokument ist ein **Anker für Gemini-Agenten**. Es ist kein
> kanonischer Inhalt. Die kanonische Quelle ist [`AGENTS.md`](AGENTS.md).
> Bei Widersprüchen gilt immer die kanonische Quelle.

## Pflicht-Leseordnung (vor jeder Aktion)

1. [`repo.meta.yaml`](repo.meta.yaml) — Repo-Verfassung
2. [`AGENTS.md`](AGENTS.md) — Bindende Leseregeln
3. [`agent-policy.yaml`](agent-policy.yaml) — Operative Steuerung
4. [`docs/roadmap.md`](docs/roadmap.md) — Strategischer Kontext
5. [`README.md`](README.md), [`docs/index.md`](docs/index.md) — Einstieg und Navigation
6. `contracts/`, `schemas/`, `.vibe/` — Verträge und Restriktionen

Bei Widersprüchen gewinnt die höhere Ebene.

## Verbote (Kurzform)

- **Keine Edits** an `repo.meta.yaml`, `AGENTS.md`, `agent-policy.yaml`,
  `.vibe/pr-scope-policy.yml` (kanonisch, handgepflegt).
- **Keine manuellen Edits** an `docs/_generated/*`, `exports/*`,
  `.cursor/rules/*` (generiert).
- **Keine Status-Änderungen** an Experimenten ohne belegte Grundlage.
- **Keine Promotion** in die Bibliothek ohne Promotion-Gate.
- **Keine erfundenen** Felder oder Konzepte außerhalb der Schemas.

## Eigen-Check

```bash
make agent-check    # schneller Diff-Guard
make validate       # vollständige Validierung
```

## Vollständige Regeln

- [`AGENTS.md`](AGENTS.md) — bindend
- [`docs/policies/agent-compliance.md`](docs/policies/agent-compliance.md) — Compliance-Übersicht
