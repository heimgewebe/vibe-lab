---
title: "Playbook: PR Run Evidence Pack"
status: active
canonicality: operative
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
schema_version: "0.1.0"
created: "2026-05-05"
updated: "2026-05-05"
author: "heimgewebe"
tags:
  - playbook
  - evidence
  - pr
---

# Playbook: PR Run Evidence Pack

> **Zweck:** Dieses Playbook beschreibt, wie ein PR Evidence-Pack Claims an konkrete Belege bindet.
> Fehlende Evidence ist ein dokumentierter Mangel und kein Erfolgsnachweis.

## A. Zweck

Ein PR Evidence-Pack dient dazu, die Kernaussagen einer PR nachvollziehbar mit Artefakten zu verknuepfen.
Es trennt klar zwischen beobachteter Ausfuehrung und Interpretation.

Leitidee:

- Claims ohne passende Evidence bleiben unbelegt.
- Ein unbelegter Claim darf nicht als PASS-Prozessclaim dargestellt werden.
- Fehlende Evidence zeigt eine Luecke, aber beweist keinen Erfolg.

## B. Grundregel

Die folgenden Regeln gelten fuer PR-Claims:

1. Kein PASS-Claim ohne starke Evidence.
2. `missing_evidence` ist kein Erfolg.
3. `external_unverified` darf keinen PASS-Prozessclaim tragen.
4. `external_verified` braucht stabile Quelle/Referenz und `sha256`.
5. `make validate`-Claims brauchen ein Command-Output-Artefakt.
6. CI-success-Claims brauchen ein CI-Artefakt oder stabil referenzierte externe Evidence.
7. Testcount-Claims brauchen ein Test-Output-Artefakt.

## C. Statusklassen

Mindestens diese Statusklassen muessen im Evidence-Pack eindeutig lesbar sein:

- `repo_local`: Artefakt liegt im Repo oder in einem repo-lokalen, stabil referenzierbaren Pfad.
- `external_verified`: Externe Evidence mit stabiler Referenz plus Hash (`sha256`) und Quelle.
- `external_unverified`: Externe Quelle ohne stabile, verifizierbare Bindung; nicht PASS-tragend.
- `missing_evidence`: Erwartete Evidence fehlt; explizit als Luecke markieren.

## D. Minimalstruktur eines Evidence-Packs (beispielhaft)

Dieses Beispiel ist eine Orientierung und **kein verbindliches Schema**:

- Run-Kontext: `run_id`, PR-Bezug, Zeitpunkt.
- Claim-Liste: pro Claim eine klare, enge Formulierung.
- Evidence-Refs: pro Claim ein oder mehrere Belegverweise mit Statusklasse.
- Bewertungsfeld: PASS/FAIL/INCONCLUSIVE nur entlang der vorhandenen Evidence.
- Gap-Hinweise: explizite Liste fehlender oder unzureichender Belege.

## E. Claim-Grenzen

Ein Evidence-Pack muss sichtbar trennen:

- **Belegt:** Aussagen mit klar zugeordneten, pruefbaren Artefakten.
- **Plausibel:** Annahmen mit Indizien, aber ohne ausreichende Belegstaerke.
- **Offen:** Punkte, zu denen aktuell keine belastbare Evidence vorliegt.
- **Nicht behauptbar:** PASS- oder Erfolgsclaims ohne die geforderte Evidenzbindung.

## F. Typische Fehlannahmen

Diese Muster sind zu vermeiden:

- "CI gruen" ohne archivierten Nachweis.
- "make validate lief" ohne Output-Artefakt.
- Screenshot oder Kommentar als starker Beleg.
- Selbstbericht als Beweis.
- `missing_evidence` als tolerierter PASS.

## G. PR-Workflow

Kurzablauf fuer jede PR:

1. Evidence-Pack vor Review aktualisieren.
2. PR-Template vollstaendig ausfuellen.
3. Fehlende Evidence explizit als fehlend markieren.
4. Keine grossen Logs ins Repo pushen; stattdessen kleine repo-lokale Artefakte oder stabile externe Referenzen nutzen.

## H. Nicht-Ziele

Dieses Playbook leistet bewusst nicht:

- kein neues Schema
- kein Validator
- keine CI-Aktivierung
- kein Agent/Skill-Wirksamkeitsclaim
- keine Behauptung von Messsystem-Reife

## Abschluss

Das Evidence-Pack ist ein Kontrollinstrument fuer Claim-Disziplin.
Es macht Belege sichtbar, markiert Luecken offen und verhindert stilles Ueberdehnen von PR-Aussagen.