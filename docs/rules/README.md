---
title: "Rules (Stub-Namespace)"
status: active
canonicality: navigation
updated: "2026-07-05"
relations:
  - type: references
    target: ../foundations/repo-plan.md
---

# Rules — Stub-Namespace

Dieser Namespace enthält aktuell nur dieses README als Stub-Marker; fachliche Artefakte liegen hier noch nicht.

**Stub-Status:** `dormant`.

- Grund: Eine neue Regelablage ohne destillierte Regel würde die kanonischen Quellen nebenbei duplizieren.
- Reaktivierung: Wenn ein Experiment, eine Synthese oder eine Decision eine neue operationalisierte Regel trägt, darf genau ein reales Regelartefakt als `minimal-seed` entstehen.
- Grenze: `dormant` bedeutet nicht `queued`; aus diesem Stub folgt keine Pflicht, den Namespace künstlich zu befüllen.

`docs/rules/` ist im Zielbaum als Ablage für **operationalisierte Regeln**
vorgesehen (`docs/foundations/repo-plan.md` → Zielstruktur, Abschnitt `docs/rules/`).
Konkrete Regeln entstehen erst, wenn ein Experiment oder eine Synthese eine
Regel destilliert, die nicht bereits in einer kanonischen Quelle
(`AGENTS.md`, `agent-policy.yaml`, `.vibe/*`, `contracts/*`, `schemas/*`)
verankert ist.

**Aktive Regelquellen** (ohne Eintrag in diesem Ordner):

- `AGENTS.md` — bindende Leseregeln für Agenten
- `.vibe/constraints.yml`, `.vibe/quality-gates.yml` — operative Verträge
- `docs/policies/` — Policy-Dokumente (Interpretation Budget, Privacy, Artifact-Boundary)
