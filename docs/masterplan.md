---
title: "Masterplan — Vibe-Lab Zielbild"
status: active
canonicality: operative
relations:
  - type: derived_from
    target: foundations/vision.md
  - type: derived_from
    target: foundations/repo-plan.md
---

# Masterplan

## Zielbild

Vibe-Lab ist ein exekutierbarer Erkenntnisraum. Das System erfasst Vibe-Coding-Hypothesen, macht sie experimentierbar, zwingt zu Entscheidungen, konserviert Lerngewinne und liefert daraus praktische, wiederverwendbare Artefakte.

## Kernprinzipien

1. **Evidenzbasiert:** Nichts wird unvalidiert zur Best Practice erklärt.
2. **Dreiphasenlogik:** Capture (rohe Ideen), Labor (freie Exploration), Bibliothek (validiertes Wissen).
3. **Pipeline:** Sammlung → Erprobung → Validierung → Kreation.
4. **Asymmetrische Rückkopplung:** Validierte Praktiken stabilisieren; Lab-Ergebnisse erzeugen Innovation; Experimente können bestehende Praktiken in Frage stellen.
5. **Selbstoptimierung:** Das System verbessert nicht nur Coding, sondern sich selbst.

## Epistemische Zustände

| Epistemischer Zustand     | Operativer Status    | Ort im Repo              |
| ------------------------- | -------------------- | ------------------------ |
| Roh                       | `idea`               | `raw-vibes/`, Issue      |
| Getestet                  | `testing`            | `experiments/`           |
| Bewährt                   | `adopted`            | `catalog/`, `prompts/`   |
| Systemisch erweitert      | (post-adoption)      | `exports/`, `instruction-blocks/` |

Sonderstatus: `blocked`, `inconclusive`, `deprecated`, `rejected`.

## Phasenmodell

- **Phase A (MVP):** Typed Intake, Experiment Engine, minimaler Katalog, Schema-Validierung, Intelligence Layer Basis.
- **Phase B (Starter Corpus):** Erstbefüllung mit Golden Example, Katalogeinträgen, Anti-Patterns, Benchmarks.
- **Phase C (Frühe Verstärker):** Instruction Blocks, Exports, Staleness, Metrik-Dashboard, Decision Artifacts.
- **Phase D (Spätphase):** Playbooks, breite Tool-Abdeckung, reaktiver Loop, Archivierung.

## Wahrheitsarchitektur

```
Kanonische Steuerungsquellen (repo.meta.yaml, AGENTS.md, agent-policy.yaml, contracts/*, schemas/*)
  ↓
Grundlagenquellen (docs/foundations/vision.md, docs/foundations/repo-plan.md)
  ↓
Operative Dokumente (README.md, CONTRIBUTING.md, .vibe/*)
  ↓
Navigation (docs/index.md)
  ↓
Diagnose (docs/_generated/*)
```

## Referenzen

- [Vision](foundations/vision.md) — Systemvision und Layer-Architektur
- [Repo-Plan](foundations/repo-plan.md) — Detaillierter Architektur- und Umsetzungsplan
- [Contribution Contract](../CONTRIBUTING.md) — Beitragstypen und Qualitätsanforderungen
