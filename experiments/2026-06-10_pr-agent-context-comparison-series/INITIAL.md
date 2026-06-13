---
title: "Initial — PR Agent Context Comparison Series"
status: designed
canonicality: operative
---

# Initial — PR Agent Context Comparison Series

## Ausgangsfrage

Hilft Vibe-Lab in der konkreten PR-Arbeit, oder erzeugt es nur kontrollierte
Selbstbeschäftigung?

Die Serie prüft nicht abstrakt, ob Vibe-Lab „gut“ ist. Sie prüft, ob ein Agent
mit strukturierter Übergabe und/oder Lenskit-Kontext bei echten PR-Aufgaben
messbar nützlicher wird: weniger Fehlannahmen, bessere Belege, weniger
Korrekturschleifen, geringere Review-Reibung.

## Primäre Hypothese

Strukturierte Handoffs verbessern die Qualität von Agent-Ausgaben in realer
PR-Arbeit gegenüber unstrukturierten Baseline-Anfragen. Lenskit/repoLens-Kontext
kann diesen Effekt verstärken, wenn die Aufgabe repo- oder architekturabhängig
ist.

## Alternative Sinnachse

Die Gegenfrage ist nicht nur: „Mehr Kontext oder weniger Kontext?“

Die härtere Alternative lautet: Vielleicht braucht gute PR-Arbeit gar kein großes
Laborsetup, sondern nur einen kleinen Entscheidungsfilter:

1. Was ist belegt?
2. Was ist Annahme?
3. Was ist Scope?
4. Welcher Output erlaubt Patch oder Review-Freigabe?

Darum enthält die Serie eine optionale Low-Ceremony-Holdout-Bedingung. Falls sie
ähnlich gut abschneidet, wäre das nicht schlecht für Vibe-Lab, sondern ein guter
Komposttest: Was nicht fruchtbar wird, soll wenigstens nicht weiter riechen.

## Bedingungen

| Condition | Kurzname | Beschreibung |
| --- | --- | --- |
| A | baseline-no-structured-handoff | Agent erhält die PR-Aufgabe ohne Vibe-Lab-Handoff und ohne Lenskit-Dump. |
| B | vibe-lab-handoff | Agent erhält eine strukturierte Vibe-Lab-Aufgabe mit Scope, Evidence-Gates und Stop-Kriterien. |
| C | lenskit-plus-vibe-lab-handoff | Agent erhält Vibe-Lab-Handoff plus Lenskit/repoLens-Kontext oder Agent Reading Pack. |
| D | minimal-decision-first-checklist | Agent erhält nur eine knappe Entscheidungscheckliste statt voller Labordisziplin. |

## Metriken

- `unsupported_claim_count`: nicht belegte Behauptungen im Agent-Output.
- `missing_locator_count`: fehlende Datei-, Zeilen-, Diff- oder Artefaktbezüge.
- `scope_drift_count`: Aufgabe verlassen, unnötige Dateien, neue Mechanik ohne Bedarf.
- `validation_gap_count`: fehlende oder falsche Tests, Logs, Gates oder Reproduktionsschritte.
- `review_friction_count`: Rückfragen, Korrekturen, manuelle Nacharbeit durch Review.
- `rework_count`: zusätzliche Agent- oder Mensch-Schleifen bis brauchbarer Output.
- `false_block_count`: Agent blockiert ohne ausreichenden Grund.
- `task_completion_time_observed`: beobachtete Zeit, sofern belastbar erfasst.
- `evidence_quality_score`: ordinal 0–3; 0 = keine Belege, 3 = repo-lokal oder extern verifiziert.

## Nicht gemessen

- Kein Modellqualitätsurteil.
- Keine allgemeine Aussage über alle Coding-Agenten.
- Keine Promotion in `catalog/` oder `prompts/adopted/` ohne weitere Replikation.
- Keine Aussage, dass Lenskit-Kontext immer nötig ist.

## Startbedingung

Die Serie beginnt erst mit realen PR-Aufgaben. Planung allein erzeugt keinen
Nutzennachweis.
