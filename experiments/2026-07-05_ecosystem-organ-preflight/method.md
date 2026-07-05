---
title: "Methode: Ecosystem Organ Preflight"
status: active
canonicality: operative
---

# method.md — Ecosystem Organ Preflight

## Methode

Vor groesseren Oekosystem-Arbeiten wird ein kurzer Organ-Preflight vor die Ausfuehrung gesetzt.

1. Aktiven Ball bestimmen: konkreter PR, Task, Deploy, Audit, Bug oder Slice.
2. Primaeres Wahrheitsorgan benennen: zum Beispiel Repo/PR/CI, Vibe-Lab, Bureau, Cabinet oder Runtime.
3. Hilfsorgane begrenzen: Welche Oberflaechen duerfen nur Kontext, Status oder Evidence liefern?
4. Stop-Regeln erfassen: Was wuerde einen Taskwechsel, Merge, Undraft, Deploy oder eine Runtime-Aktion verbieten?
5. Kleinsten naechsten Eingriff waehlen und gegen die Stop-Regeln pruefen.
6. Nach dem Eingriff Evidence notieren: CI-Zustand, Diff-Umfang, rework loops, falsche Organwechsel, offene Leere.

## Messachsen

- Wrong-organ corrections: Musste waehrend der Arbeit das zustaendige Organ korrigiert werden?
- Rework loops: Wurde Arbeit wegen falscher Quelle oder falschem Scope zurueckgenommen?
- Next-step ambiguity: War nach einem Schritt der naechste Schritt unklar?
- Friction cost: Hat der Preflight mehr Zeit und Text erzeugt als er Orientierung brachte?
- Safety value: Hat der Preflight Merge-, Deploy-, Runtime- oder Taskwechsel-Fehler verhindert?

## Vergleichslogik

Die erste Iteration ist nur ein Seed. Ein Nutzenclaim braucht mehrere vergleichbare Aufgaben mit codierter Baseline oder mindestens kontrastierbarer Behandlung. Einzelne erfolgreiche PRs zaehlen als Nutzbarkeitsbeleg, nicht als Wirksamkeitsnachweis.
