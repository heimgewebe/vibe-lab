---
title: "Decisions/Export (Stub-Namespace)"
status: active
canonicality: navigation
updated: "2026-05-18"
relations:
  - type: references
    target: ../../docs/foundations/repo-plan.md
---

# Decisions / Export — Stub-Namespace

Dieser Namespace enthält aktuell nur dieses README als Stub-Marker; fachliche Artefakte liegen hier noch nicht.

`decisions/export/` ist Teil der **typisierten Decision-Namespaces**
(`process/`, `system/`, `export/`, `policy/`, `benchmark/`), die im Repo-Plan
als Phase-C-Verstärker angelegt sind
(`docs/foundations/repo-plan.md` → „Typisierte Decision Artifacts").

**Zweck:** Hier landen Decision Artifacts, die sich auf Export-Targets
(`exports/copilot/`, `exports/cursor/`, weitere Tool-Ausleitungen) beziehen
— z. B. Aufnahme oder Stilllegung eines Target-Tools, Änderungen am
Sanitization-Prinzip für Exports, Format-Migrationen.

Bislang sind keine solchen Entscheidungen formal abgelegt. Aktive Export-Logik
ist verankert in:

- `.vibe/generated-artifacts.yml` (objektbasierter Klassifikator)
- `scripts/exports/generate_exports.py` (Generator + Header-Format)
- `scripts/exports/validate_export_parity.py` (Konflikt-Gate, CI-blocking)

**Schema:** Decision-Artifacts ohne `decisions/system/`-Bezug haben aktuell
**keinen** Pflicht-Contract. Erst beim ersten realen Eintrag wird entschieden,
ob ein eigener Schema-Strang sinnvoll ist.
