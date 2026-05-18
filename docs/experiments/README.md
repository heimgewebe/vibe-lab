---
title: "Docs/Experiments (Stub-Namespace)"
status: active
canonicality: navigation
updated: "2026-05-18"
relations:
  - type: references
    target: ../foundations/repo-plan.md
  - type: references
    target: ../../experiments/README.md
---

# Docs/Experiments — Stub-Namespace

Dieser Ordner ist absichtlich leer.

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
