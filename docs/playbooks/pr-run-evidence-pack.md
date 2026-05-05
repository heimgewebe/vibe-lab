---
title: "Playbook: PR Run Evidence Pack"
status: active
canonicality: operative
schema_version: "0.1.0"
created: "2026-05-05"
updated: "2026-05-05"
author: "heimgewebe"
relations:
  - type: references
    target: ../policies/pr-run-evidence-policy.md
  - type: references
    target: ../policies/artifact-boundary-policy.md
  - type: references
    target: ../policies/interpretation-budget.md
  - type: references
    target: evidence-control-plane-roadmap-checklist.md
  - type: references
    target: reconciliation.md
tags:
  - playbook
  - evidence
  - pr
---

# Playbook: PR Run Evidence Pack

> Zweck: Ein PR Run Evidence Pack bindet konkrete Claims an konkrete Evidence.
> Fehlende Evidence ist kein Erfolgssignal, sondern ein dokumentierter Mangel.

## A. Zweck

Das PR Run Evidence Pack wird vor einem PR-Review gepflegt und zusammen mit den Claim-Texten betrachtet.

Es soll sicherstellen:

- Claims sind an benannte Evidence-Artefakte gebunden.
- Die Beleglage ist pro Claim sichtbar.
- Fehlende Belege werden als fehlend markiert statt als Erfolg umgedeutet.

Wichtig: Wenn Evidence fehlt, beweist das Pack keinen Erfolg. Es dokumentiert nur, was belegt ist und was offen bleibt.

## B. Grundregel

1. Kein PASS-Claim ohne starke Evidence.
2. `missing_evidence` ist kein Erfolg.
3. `external_unverified` darf keinen PASS-Prozessclaim tragen.
4. `external_verified` braucht stabile Quelle/Referenz und Hash.
5. `make validate`-Claims brauchen Command-Output-Artefakt.
6. CI-success-Claims brauchen CI-Artefakt oder stabil referenzierte externe Evidence.
7. Testcount-Claims brauchen Test-Output-Artefakt.

Diese Regeln operationalisieren die Grenzen aus den referenzierten Policies, ohne hier ein technisches Enforcement zu behaupten.

## C. Statusklassen

- `repo_local`: Evidence liegt im Repo oder in klar referenzierten, repo-lokalen Artefakten vor.
- `external_verified`: Evidence liegt extern, aber mit stabiler Referenz (z. B. URL/Run-ID) und Integritaetsnachweis (z. B. `sha256`) vor.
- `external_unverified`: Evidence liegt extern ohne stabile, verifizierbare Referenz vor; geeignet fuer Hinweise, nicht fuer PASS-Claims.
- `missing_evidence`: Fuer den Claim liegt kein belastbarer Beleg vor.

## D. Minimalstruktur eines Evidence-Packs (exemplarisch)

Die folgende Struktur ist ein Beispiel zur Orientierung, kein verbindliches Schema:

```yaml
run_id: "2026-05-05-pr3-docs"
claims:
  - id: "claim.validate.green"
    text: "make validate lief erfolgreich"
    status: "repo_local"
    evidence_refs:
      - path: "artifacts/validate-output.txt"
        kind: "command_output"
  - id: "claim.ci.success"
    text: "CI war gruen"
    status: "external_verified"
    evidence_refs:
      - source: "https://example.invalid/run/123"
        sha256: "..."
```

Erwartung an die Dokumentation:

- Jeder Claim hat einen Status.
- Jeder PASS-nahe Claim hat nachvollziehbare Evidence-Referenzen.
- Fehlende Evidence wird explizit markiert.

## E. Claim-Grenzen

Ein Evidence-Pack muss klar trennen:

- Was belegt ist.
- Was nur plausibel ist.
- Was offen bleibt.
- Was nicht behauptet werden darf.

Nicht zulaessig sind Formulierungen, die fehlende oder unverifizierte Evidence als bestaetigten Erfolg framen.

## F. Typische Fehlannahmen

- "CI gruen" ohne archivierten Nachweis.
- "make validate lief" ohne Output-Artefakt.
- Screenshot oder Kommentar als starker Beleg.
- Selbstbericht als Beweis.
- `missing_evidence` als tolerierter PASS.

Diese Muster sind fuer Reviews rote Flaggen und muessen als Claim/Evidence-Gap behandelt werden.

## G. PR-Workflow

1. Evidence-Pack vor Review aktualisieren.
2. PR-Template vollstaendig ausfuellen.
3. Fehlende Evidence als fehlend markieren, nicht kaschieren.
4. Keine grossen Logs ins Repo pushen; stattdessen kleine repo-lokale Artefakte oder stabile externe Referenzen nutzen.

## H. Nicht-Ziele

Dieses Playbook fuehrt nicht ein:

- kein neues Schema
- kein Validator
- keine CI-Aktivierung
- kein Agent/Skill-Wirksamkeitsclaim
- keine Behauptung von Messsystem-Reife
