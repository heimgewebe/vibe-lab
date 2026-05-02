---
title: "Blueprint — Evidence-Control-Plane v1"
status: draft
canonicality: exploratory
created: "2026-05-02"
updated: "2026-05-02"
author: "GitHub Copilot"
triggered_by: "user-request-evidence-control-plane-pr1-2026-05-02"
relations:
  - type: references
    target: "../policies/interpretation-budget.md"
  - type: references
    target: "../blueprints/blueprint-agent-operability.md"
  - type: references
    target: "../playbooks/evidence-control-plane-roadmap-checklist.md"
tags:
  - blueprint
  - evidence
  - control-plane
  - draft
---

# Blueprint — Evidence-Control-Plane v1

> **Status:** `draft` — `canonicality: exploratory`
>
> Diese Blaupause beschreibt ein geplantes Kontrollsystem, das noch nicht existiert.
> Die Evidence-Control-Plane ist **nicht aktiv**. Es existieren derzeit weder Policy,
> Schema, Validator noch CI-Erweiterung. Dieser Blueprint ist Entwurfsgrundlage,
> keine operative Aussage.
>
> Kein Wirksamkeitsclaim zur Agenten- oder Skill-Schicht.

---

## Zweck

Ziel der Evidence-Control-Plane ist es, Claims in PR-Beschreibungen, Experiment-
Manifesten und Commit-Nachrichten an nachvollziehbare Evidenz zu koppeln — bevor
sie in kanonischen Dokumenten oder Promotions landen.

**Nicht-Ziele (explizit):**

- Keine Behauptung, dass Agenten oder Skills dadurch wirksamer oder zuverlässiger werden.
- Kein automatisiertes Enforcement zum jetzigen Zeitpunkt.
- Kein Claim, dass dieser Blueprint die einzig mögliche Architektur darstellt.
- Kein Ersatz für die bestehende Policy (`interpretation-budget.md`).
- Keine Aussage über Cross-Run-Assessment oder Claim-Kausalität.

---

## Problem

Aktuell fehlt eine strukturierte Kopplung zwischen:

1. **Claims** (Aussagen in PR-Texten, Manifest-Feldern, Commit-Nachrichten)
2. **Evidenz** (Beobachtete Ausführungsspuren, `evidence.jsonl`, Artefakte)

Ohne diese Kopplung können Claims unbemerkt aus dem Evidenzraum herausdriften —
insbesondere an der Grenze zwischen Experiment-Lab und Promotions.

---

## Architekturskizze

```
PR-Text / Manifest-Claim
        ↓
  [Claim-Evidence-Validator]  ← noch nicht implementiert
        ↓
  evidence.jsonl / run-bundle
        ↓
  PR-Scope-Guard              ← noch nicht implementiert
        ↓
  Promotion / catalog/
```

Alle Komponenten in eckigen Klammern sind **geplant**, nicht vorhanden.

### Geplante Komponenten (Übersicht)

| Komponente              | Zweck                                                    | Status     |
| ----------------------- | -------------------------------------------------------- | ---------- |
| Evidence-Pack-Schema    | Maschinenlesbares Schema für Evidenz-Bündel              | geplant    |
| Claim-Evidence-Validator| Prüft Claim→Evidenz-Kopplung                             | geplant    |
| Run-Bundle-Kopplung     | Verbindet PR-Run mit Evidence-Pack                       | geplant    |
| PR-Scope-Guard          | Blockiert Promotion ohne validierte Evidenz              | geplant    |
| PR-Template-Härtung     | Erzwingt Evidenz-Pflichtfelder in PR-Beschreibungen      | geplant    |

---

## Zielmetriken

Diese Metriken sind **Planungsgrößen**, keine Messergebnisse:

- Anteil PRs mit maschinenlesbarem Evidence-Pack: **Ziel: 100 % ab PR 6**
- Anteil Promotions mit validierter Claim→Evidenz-Kopplung: **Ziel: 100 % ab PR 5**
- Anteil unbelegter Claims in Manifest-Feldern nach PR 7: **Ziel: 0 %**

Die Metriken gelten erst als messbar, wenn die zugehörigen Validatoren und
Fixtures existieren und in CI laufen.

---

## Falsifikationskriterien

Diese Kriterien definieren, wann der Blueprint als gescheitert gilt:

1. **Validator nicht implementierbar:** Das geplante Claim-Evidence-Schema lässt
   sich nicht in valide JSON Schema überführen, ohne die bestehende
   Manifest-Struktur zu brechen.

2. **Kopplung zu rigid:** PR-Scope-Guard blockiert legitime Promotions aufgrund
   von Randfall-Claims, die keine direkte Evidenz erfordern (z. B. reine
   Refactorings).

3. **Adoption zu gering:** Nach 3 kontrollierten Runs (PR 9+) zeigt sich, dass
   Claim-Kopplung keinen messbaren Effekt auf Overclaiming-Rate hat.

4. **Technische Inkompatibilität:** Run-Bundle-Kopplung ist mit dem bestehenden
   `evidence.jsonl`-Format nicht vereinbar ohne breaking Schema-Änderung.

Tritt eines dieser Kriterien ein, ist der Blueprint zu revidieren oder zu
verwerfen — nicht stillschweigend weiterzuführen.

---

## Umsetzungsmodus

Die Umsetzung erfolgt schrittweise über separate, validierte PRs.
Der aktuelle Stand ist in der Roadmap dokumentiert:

→ [`docs/playbooks/evidence-control-plane-roadmap-checklist.md`](../playbooks/evidence-control-plane-roadmap-checklist.md)

**PR 1** (dieser Scaffold) deckt ausschließlich:
- Blueprint-Dokument (dieses Dokument)
- Roadmap-Checklist
- Navigation in `docs/index.md`

Enforcement, Schemas, Validator-Code, Policy-Implementierung und neue
Experiment-Runs sind nicht Bestandteil von PR 1 und bleiben in späteren PRs.

---

## Abgrenzung zu bestehenden Mechanismen

| Bestehendes Artefakt          | Verhältnis                                           |
| ----------------------------- | ---------------------------------------------------- |
| `policies/interpretation-budget.md` | Bestehende Guard-Policy bei Promotion; bleibt unverändert |
| `schemas/experiment.manifest.schema.json` | Bestehendes Manifest-Schema; wird nicht geändert |
| `contracts/docmeta.schema.json` | Bestehendes Frontmatter-Schema; wird nicht geändert |
| `scripts/docmeta/validate_interpretation_budget.py` | Bestehender Validator; wird nicht geändert |

Die Evidence-Control-Plane ergänzt diese Mechanismen perspektivisch — sie
ersetzt nichts und greift erst, wenn die geplanten Komponenten implementiert sind.
