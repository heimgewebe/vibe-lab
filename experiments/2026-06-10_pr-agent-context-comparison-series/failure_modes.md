---
title: "Failure Modes — PR Agent Context Comparison Series"
status: designed
canonicality: operative
---

# Failure Modes — PR Agent Context Comparison Series

## 1. Task-Difficulty dominiert Condition

**Risiko:** Eine schwere Aufgabe unter Condition A wirkt schlechter als eine
leichte Aufgabe unter Condition C.

**Guardrail:** Task-Klasse, PR-Größe, betroffene Dateien und erforderlicher
Repo-Kontext müssen in `comparability.yml` dokumentiert werden.

## 2. Lenskit-Kontext wird als Wahrheit behandelt

**Risiko:** Agent zitiert Navigation statt kanonische Quelle, Code, Diff oder Log.

**Guardrail:** Condition C muss explizit festhalten: Lenskit/Agent-Pack ist
Navigation, nicht Evidenz. Claims brauchen kanonische oder repo-lokale Belege.

## 3. Labordisziplin erzeugt Scheinsicherheit

**Risiko:** Viele Artefakte wirken wie Qualität, obwohl der Output inhaltlich
schwach bleibt.

**Guardrail:** `measurement.yml` zählt Review-Friction, Rework und unsupported
claims. Artefaktvollständigkeit allein darf kein PASS begründen.

## 4. Reviewer-Learning verfälscht Ergebnis

**Risiko:** Spätere Runs werden besser, weil der Mensch bessere Aufgaben stellt
oder den Agenten besser steuert.

**Guardrail:** Condition-Reihenfolge rotieren; Rehearsal-Effekte markieren;
keine starken Claims aus sequenziellen Einzelbeobachtungen.

## 5. Baseline wird unfair schwach gemacht

**Risiko:** Condition A erhält absichtlich zu wenig Kontext und verliert dadurch
trivial.

**Guardrail:** Baseline muss realistischen Arbeitsalltag abbilden. Sie darf nicht
künstlich dumm gemacht werden. Auch ein Kontrollhamster verdient ein faires Rad.

## 6. Patch-Erfolg wird mit Erkenntnis verwechselt

**Risiko:** Ein Patch geht durch, aber die Condition hat nur Glück gehabt.

**Guardrail:** Patch-Akzeptanz ist eine Messgröße, aber kein alleiniger
Nutzennachweis. Fehlerarten und Belegqualität müssen mitbewertet werden.

## 7. Zu frühe Adoption

**Risiko:** Nach einem guten Run wird ein Workflow in `catalog/` oder
`prompts/adopted/` übernommen.

**Guardrail:** Keine Adoption ohne `result_assessment`, Cross-Run-Assessment und
Interpretation Budget. Einzelruns bleiben Beobachtungen.
