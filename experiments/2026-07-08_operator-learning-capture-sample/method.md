---
title: "Methode: Operator Learning Capture Sample"
status: active
canonicality: operative
---

# method.md — Operator Learning Capture Sample

## Methode

1. Nimm wenige aktuelle, abgeschlossene oder fortgeschrittene Oekosystem-Arbeiten als Sample.
2. Nutze nur vorhandene Artefakte: PR-Bodies, PR-Status, Validierungsangaben, Review-Hinweise, Registry- oder Run-Belege.
3. Codiere nicht die ganze Arbeit, sondern nur Reibungsereignisse und Claim-Grenzen.
4. Trenne beobachtete Evidenz, plausible Interpretation und nicht belegte Wirkung.
5. Entscheide, ob ein formaler Capture-Contract gerechtfertigt ist.

## Coding-Achsen

| Feld | Bedeutung |
| --- | --- |
| `source` | Repo/PR/Artefakt, aus dem die Beobachtung stammt. |
| `observed_signal` | Enger, beobachteter Reibungs- oder Lernhinweis. |
| `evidence_boundary` | `observed`, `self_reported`, `inferred`, `stale`, `missing`, `unknown`. |
| `candidate_pattern` | Moegliches wiederkehrendes Muster, noch kein Claim. |
| `followup_owner` | Organ, das bei bestaetigtem Muster spaeter handeln sollte. |
| `non_claims` | Was aus dem Sample ausdruecklich nicht folgt. |

## Bewertungslogik

Das Sample ist erfolgreich, wenn es eine klare Antwort auf diese Frage liefert:

> Reicht vorhandene Evidenz aus, um einen kleinen, spaeter automatisierbaren Learning-Capture-Contract zu rechtfertigen?

Es ist nicht erfolgreich, wenn:

- keine wiederkehrende Reibung sichtbar wird;
- alle Erkenntnisse nur subjektiv aus Chat-Kontext rekonstruierbar sind;
- die manuelle Erfassung schwerer wirkt als der erwartbare Nutzen;
- Vibe-Lab dadurch faktisch Steuerungs- oder Priorisierungshoheit erhaelt.

## Claim-Grenze

Ein einzelnes Sample darf nur Nutzbarkeits- und Architekturhinweise liefern.

Es belegt nicht:

- dass Vibe-Lab die Arbeit verbessert;
- dass Rework sinkt;
- dass Grabowski geaendert werden muss;
- dass Bureau- oder Leitstand-Integration schon produktiv sinnvoll ist.
