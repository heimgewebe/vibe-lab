---
title: "Docs/Experiments (Stub-Namespace)"
status: active
canonicality: navigation
updated: "2026-07-05"
relations:
  - type: references
    target: ../foundations/repo-plan.md
  - type: references
    target: ../../experiments/README.md
---

# Docs/Experiments — Stub-Namespace

Dieser Namespace enthält aktuell nur dieses README als Stub-Marker; fachliche Artefakte liegen hier noch nicht.

**Stub-Status:** `dormant`.

- Grund: Das operative Labor liegt unter `/experiments/`; diese Dokumentationsebene hat noch kein eigenes freigegebenes Versuchsdesign-Artefakt.
- Reaktivierung: Wenn ein reales Versuchsdesign bewusst auf der Dokumentationsebene geführt werden soll, darf genau ein konkretes Design-Artefakt als `minimal-seed` entstehen.
- Grenze: `dormant` bedeutet nicht `queued`; aus diesem Stub folgt keine Pflicht, den Namespace künstlich zu befüllen.

`docs/experiments/` ist im Zielbaum als **Dokumentationsebene für
Versuchsdesign** vorgesehen (`docs/foundations/repo-plan.md` → Zielstruktur,
Abschnitt `docs/experiments/`). Er ist **nicht** identisch mit dem operativen
Labor unter [`/experiments/`](../../experiments/README.md), in dem konkrete
Experiment-Bundles liegen.

**Trennung der Räume:**

| Pfad | Inhalt | Validierung |
| ---- | ------ | ----------- |
| `/experiments/<datum>_<name>/` | Konkrete Experiment-Bundles (`manifest.yml`, `evidence.jsonl`, ...) | Schema-Validierung, Promotion-Gate |
| `docs/experiments/` (dieser Ordner) | Übergeordnete Design-Notizen, Versuchsklassen, methodische Reflexionen | docmeta-Frontmatter |

Bisher wurden methodische Reflexionen entweder direkt in Experiment-CONTEXT,
in `docs/concepts/` oder in `docs/evaluations/` abgelegt. Dieser Stub bleibt
offen, falls ein eigener Bedarf entsteht.
