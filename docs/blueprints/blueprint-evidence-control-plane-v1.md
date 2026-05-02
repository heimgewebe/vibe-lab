---
title: "Blueprint — Evidence-Control-Plane v1"
status: draft
canonicality: exploratory
relations:
  - type: references
    target: blueprint-agent-operability.md
  - type: references
    target: blueprint-agent-skill-minimal-layer-v0.1.md
  - type: references
    target: ../policies/interpretation-budget.md
---

# Blueprint — Evidence-Control-Plane v1

## Problem
Claims zu PASS/Erfolg sind heute teilweise als Prosa formulierbar, ohne zwingende, archivierte, maschinenlesbare Evidenzbindung.

## Zielbild
Ein Repo-Zustand, in dem Claims nicht geglaubt, sondern gegen Evidence geprüft werden:

1. Claim wird extrahiert.
2. Claim wird einem Claim-Typ zugeordnet.
3. Claim wird nur mit zulässigem Evidence-Status akzeptiert.
4. Fehlende oder widersprüchliche Evidence führt zu MISSING_EVIDENCE bzw. CONTRADICTION.

## Nicht-Ziele
- Keine Aussage, dass Agenten/Skill-Schicht bereits wirksam oder „nützlich“ ist.
- Kein Ersatz der kanonischen Steuerungsquellen.
- Keine implizite Aktivierung von Enforcement nur durch Blueprint- oder Playbook-Text.

## Architektur (Soll)
- Autoritätsschicht bleibt unverändert (kanonische Quellen).
- Evidence-Pack als maschinenlesbarer Contract pro Run.
- Claim-Lint als Guard gegen unbelegte Prozess- und Mengenclaims.
- Scope/Artifact-Boundary-Guards gegen Selbstmessung und Artefaktblähung.
- Artifact-Boundary: große Logs, Full-Diffs und externe Dumps werden nicht repo-lokal als Primärevidence committet; lokal bleiben Summary, Hash und Herkunft.

## Falsifikationskriterien
Die Blaupause gilt nach mindestens drei neuen PRs unter dieser Roadmap als unzureichend, wenn:

- `evidence_pack_completeness < 0.85`
- `external_unverified_ratio > 0.30`
- `contradiction_count > 0` erst nach Merge erkannt wird
- `validation_gap_count` gegenüber dem Startwert nicht sinkt
- Review-Reibung stark steigt, ohne dass `claim_to_evidence_binding_rate` besser wird
- Missing-Evidence-Placeholder echte Evidence nur simulieren

## Zielmetriken

- `claim_to_evidence_binding_rate`
- `unsupported_claim_count`
- `validation_gap_count`
- `contradiction_count`
- `external_unverified_ratio`
- `evidence_pack_completeness`
- `self_observation_violation_count`
- `artifact_boundary_violation_count`

## Umsetzungsmodus
Die konkrete Reihenfolge ist in der operativen Roadmap beschrieben:
`docs/playbooks/evidence-control-plane-roadmap-checklist.md`.
