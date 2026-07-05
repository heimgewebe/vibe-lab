---
title: "Decisions/Export (Stub-Namespace)"
status: active
canonicality: navigation
updated: "2026-07-05"
relations:
  - type: references
    target: ../../docs/foundations/repo-plan.md
---

# Decisions / Export — Stub-Namespace

Dieser Namespace enthält aktuell nur dieses README als Stub-Marker; fachliche Artefakte liegen hier noch nicht.

**Stub-Status:** `dormant`.

- Grund: Export-Logik ist aktuell über bestehende Artefaktverträge abgedeckt; kein eigener Export-Decision-Fall erzwingt diesen Namespace.
- Reaktivierung: Wenn ein realer Export-Target- oder Format-Migrationsentscheid ansteht, darf genau ein konkretes Decision-Artefakt als `minimal-seed` entstehen.
- Grenze: `dormant` bedeutet nicht `queued`; aus diesem Stub folgt keine Pflicht, den Namespace künstlich zu befüllen.

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
