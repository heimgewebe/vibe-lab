---
title: "Methode: Ecosystem Organ Preflight"
status: active
canonicality: operative
---

# method.md - Ecosystem Organ Preflight

## Methode

Vor groesseren Oekosystem-Arbeiten wird ein kurzer Organ-Preflight vor die Ausfuehrung gesetzt.

1. Aktiven Ball bestimmen: konkreter PR, Task, Deploy, Audit, Bug oder Slice.
2. Primaeres Wahrheitsorgan benennen: zum Beispiel Repo/PR/CI, Vibe-Lab, Bureau, Cabinet oder Runtime.
3. Quellenfrische pruefen: PR-Head, Base-SHA, lokale Branch-Lage, CI-Status und verwendete Dumps gegen den aktuellen Arbeitsstand abgleichen.
4. Hilfsorgane begrenzen: Welche Oberflaechen duerfen nur Kontext, Status oder Evidence liefern?
5. Stop-Regeln erfassen: Was wuerde einen Taskwechsel, Merge, Undraft, Deploy oder eine Runtime-Aktion verbieten?
6. Kleinsten naechsten Eingriff waehlen und gegen die Stop-Regeln pruefen.
7. Nach dem Eingriff Evidence notieren: CI-Zustand, Diff-Umfang, rework loops, falsche Organwechsel, offene Leere.

## Messachsen

| Metric | Type | Coding |
| --- | --- | --- |
| `wrong_organ_corrections` | integer | Jede explizite Korrektur des zustaendigen Organs oder der primaeren Wahrheitsquelle waehrend einer Aufgabe. |
| `rework_loops` | integer | Zurueckgenommene oder wiederholte Arbeit, die durch falsche Quelle, falschen Scope oder falsches Organ entstanden ist. |
| `next_step_ambiguity` | enum | `none`, `low`, `medium`, `high` nach einem Eingriff. |
| `friction_cost_minutes` | number | Geschaetzte Zusatzminuten, die der Preflight selbst erzeugt. |
| `safety_value` | enum | `none`, `low`, `medium`, `high`; kurze Begruendung im Run-Budget. |

## Vergleichslogik

Die erste Iteration ist nur ein Seed. Ein Nutzenclaim braucht mehrere vergleichbare Aufgaben mit codierter Baseline oder mindestens kontrastierbarer Behandlung. Einzelne erfolgreiche PRs zaehlen als Nutzbarkeitsbeleg, nicht als Wirksamkeitsnachweis.
