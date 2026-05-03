---
title: "Policy — PR Run Evidence"
status: draft
canonicality: exploratory
relations:
  - type: references
    target: ../blueprints/blueprint-evidence-control-plane-v1.md
  - type: references
    target: ../playbooks/evidence-control-plane-roadmap-checklist.md
  - type: references
    target: interpretation-budget.md
---

# Policy — PR Run Evidence

> Status: `draft` / `exploratory`
>
> Diese Policy ist noch nicht technisch enforced.
> Sie definiert normative Grenzen, aktiviert aber kein technisches Enforcement.

## Normative Grenzen

- Keine aktive Enforcement-Regel ohne Schema/Script/Make/CI-Integration.
- Kein Wirksamkeitsclaim zur Agent/Skill-Schicht.
- No PASS without archived evidence.
- Ein PASS-Claim braucht ein existierendes, referenziertes Evidenzartefakt.
- `missing_evidence`, `external_unverified`, `self_reported`, `unknown` duerfen keinen PASS-Prozessclaim tragen.
- Missing-Evidence-Placeholder dokumentieren Abwesenheit, beweisen aber keinen Erfolg.
- Kein quantitativer Testcount-Claim ohne Test-Output-Artefakt.
- Kein CI-success-Claim ohne archivierte CI-Evidence.
- Kein `make validate`-Claim ohne Command-Output-Artefakt.
- Kein Critic-/Auditor-Usage-Claim ohne archiviertes Agent-Output-Artefakt.
- PR-Body-Claims muessen auf Evidence-Artefakte verweisen oder ausdruecklich als nicht belegt markiert werden.

## Nicht-Ziel dieser Policy

- Keine unmittelbare Aktivierung von Blockern in CI oder lokalen Validatoren durch dieses Dokument allein.
