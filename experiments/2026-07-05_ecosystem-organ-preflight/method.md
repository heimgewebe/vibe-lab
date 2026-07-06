---
title: "Methode: Ecosystem Organ Preflight"
status: active
canonicality: operative
---

# method.md — Ecosystem Organ Preflight

## Methode

Vor größeren Ökosystem-Arbeiten wird ein kurzer Organ-Preflight vor die Ausführung gesetzt.

1. Aktiven Ball bestimmen: konkreter PR, Task, Deploy, Audit, Bug oder Slice.
2. Primäres Wahrheitsorgan benennen: zum Beispiel Repo/PR/CI, Vibe-Lab, Bureau, Cabinet oder Runtime.
3. Quellenfrische prüfen: PR-Head, Base-SHA, lokale Branch-Lage, CI-Status und verwendete Dumps gegen den aktuellen Arbeitsstand abgleichen.
4. Hilfsorgane begrenzen: Welche Oberflächen dürfen nur Kontext, Status oder Evidence liefern?
5. Stop-Regeln erfassen: Was würde einen Taskwechsel, Merge, Undraft, Deploy oder eine Runtime-Aktion verbieten?
6. Kleinsten nächsten Eingriff wählen und gegen die Stop-Regeln prüfen.
7. Nach dem Eingriff Evidence notieren: CI-Zustand, Diff-Umfang, rework loops, falsche Organwechsel, offene Leere.

## Messachsen

| Metric | Type | Coding |
| --- | --- | --- |
| `wrong_organ_corrections` | integer | Zähle jede explizite Korrektur des zuständigen Organs oder der primären Wahrheitsquelle während einer Aufgabe. |
| `rework_loops` | integer | Zähle zurückgenommene oder wiederholte Arbeit, die durch falsche Quelle, falschen Scope oder falsches Organ entstanden ist. |
| `next_step_ambiguity` | enum | `none`, `low`, `medium`, `high` nach einem Eingriff; kodiert die Unklarheit des nächsten Schritts. |
| `friction_cost` | integer_minutes | Geschätzte Zusatzminuten, die der Preflight selbst erzeugt. |
| `safety_value` | enum | `none`, `potential`, `actual`; mit kurzer Begründung, ob ein Merge-, Deploy-, Runtime- oder Taskwechsel-Fehler verhindert wurde. |

## Vergleichslogik

Die erste Iteration ist nur ein Seed. Ein Nutzenclaim braucht mehrere vergleichbare Aufgaben mit codierter Baseline oder mindestens kontrastierbarer Behandlung. Einzelne erfolgreiche PRs zählen als Nutzbarkeitsbeleg, nicht als Wirksamkeitsnachweis.
