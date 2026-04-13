---
title: "Experiment-Ergebnis: Pretty Evidence Script"
status: adopted
canonicality: operative
---

# result.md — Experiment-Ergebnis

> Führt Beweise und Deutung zusammen. Hier entsteht neues Wissen.

## Rohdaten (Beweise)

> Fakten aus `evidence.jsonl`. Was ist passiert?

- Ein Skript `scripts/pretty_evidence.py` wurde erstellt.
- Das Skript wurde erfolgreich mit `experiments/2026-04-13_pretty-evidence-script/results/evidence.jsonl` aufgerufen.
- Das Ergebnis wurde nach `experiments/2026-04-13_pretty-evidence-script/artifacts/test_output.txt` geschrieben (Log-Eintrag `run` in `evidence.jsonl`).
- Ein `observation`-Log-Eintrag wurde in `evidence.jsonl` hinterlegt.
- `make validate` war erfolgreich.

## Deutung (Interpretation)

> Was bedeuten diese Daten für die Hypothese?

- **Wo das Repo zu sauberem Denken gezwungen hat:** Der Zwang, einen gültigen Proof-of-Run in `evidence.jsonl` als `run`-Event zu hinterlegen, verhinderte, dass die blosse Erstellung des Skripts als "Erfolg" verbucht wird. Es musste tatsächlich ein Artefakt produziert und dieses verlinkt werden.
- **Wo Struktur geholfen hat:** Das strikte Trennen von Kontext, Methode, und Resultat sowie die Überprüfung mittels `make validate` machte den Prozess transparent und strukturiert.
- **Wo Struktur Reibung erzeugt hat:** Für ein sehr kurzes Python-Skript (ca. 45 Zeilen) war der Dokumentationsaufwand (Manifest, Context, Method, Initial, Evidence.jsonl, Result) vergleichsweise hoch. Man muss viele Dateien "mitziehen", auch wenn das eigentliche Tool extrem simpel ist.
- **Epistemische Aufwertung:** Es gab keine Versuchung, das Skript ohne echten Run aufzuwerten, da die Regeln (z. B. fehlendes `artifact_ref` führt zu Validierungsfehlern) dies technisch und prozedural verhindern.

## Konklusion

Das Repo zwingt durch seine harten Invarianten (Schemas, Relationen, Beweis-Pflicht) zu einer epistemisch sauberen Arbeitsweise. Auch bei unterbestimmten Aufgaben wird der Agent in ein Raster aus Beobachtung, Run-Logs und expliziter Deutung gedrängt. Die Hypothese wird bestätigt.

## Nächste Schritte

- Entscheidung (Decision Artifact) anlegen (Adopt).
- Das Skript im Projektverlauf für Diagnosen nutzen.

## Reflexion (Metrik-Fokus)
- **Was hat gut funktioniert?** Der Validierungsprozess war klar und hat sofort aufgezeigt, wenn Abhängigkeiten (wie `pyyaml`) gefehlt haben. Das Trennen der "Warum"-Ebene (Context) von der "Wie"-Ebene (Method) von der "Was"-Ebene (Result) ist stark.
- **Was war unklar?** Es ist manchmal eine Gratwanderung, wie detailliert man kleine Schritte in `evidence.jsonl` aufnimmt.
- **Gerechtfertigte Verbesserungen:** Ein Make-Target, um direkt `pretty_evidence.py` für das letzte/aktuelle Experiment auszuführen.
- **Verfrühte Verbesserungen:** Ein komplexes CLI-Tool für `evidence.jsonl` zu bauen, bevor die Basisstruktur stabil ist.
