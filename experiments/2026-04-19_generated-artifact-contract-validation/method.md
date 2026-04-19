---
title: "Methode: Generated Artifact Contract Validation"
status: draft
canonicality: operative
---

# method.md — Experiment-Methode

> Beschreibt das strukturierte Vorgehen zur Prüfung der Hypothese.

## Hypothese

Wenn das Contract-Modell `canonical/derived/ephemeral` plus CI-Split `blocking/non-blocking/artifact-only` korrekt wirkt, dann sinken gegenueber dem frueheren Zustand:

- CI-Fails durch nicht kritische Diagnosedrift
- manuelle Nacharbeit pro PR
- wahrgenommene Unsicherheit bei Fehlerdiagnose

## Methode

### Vorgehen

1. Baseline definieren (letzte 2 bis 3 PRs vor Contract-Split, soweit verfuegbar).
2. Mindestens 2 reale PRs unter neuem Contract-System durchlaufen.
3. Pro PR erfassen:
	- Drift in `canonical`, `derived`, `ephemeral`
	- betroffene CI-Jobs und deren Ausgang
	- notwendige manuelle Eingriffe (Regen, Commit-Nachzug, Re-Run)
4. Beobachtungen strukturiert in `results/evidence.jsonl` loggen.
5. Vergleich Baseline vs. neues System in `results/result.md` dokumentieren.

### Metriken

- **Contract Adherence:** Anzahl Contract-Verletzungen pro PR (nach Klasse).
- **CI-Friction:** Anzahl blockierender CI-Fehler, die auf Diagnoseartefakte zurueckgehen.
- **Manual Intervention Count:** Anzahl manueller Korrekturen fuer Generated-Artifacts.
- **Diagnosis Clarity Score (1-5):** subjektive Klarheit, welcher Job warum fehlschlug.
- **Unnecessary Commit Delta:** Commits nur fuer nicht-kritische Drift.

### Erfolgskriterien

- Mindestens 30% weniger blockierende CI-Friction gegen Baseline.
- Keine Fehlblocker durch `derived` oder `ephemeral` Artefakte.
- Manual Intervention Count sinkt oder bleibt bei hoehherer Diagnoseklarheit stabil.
- Bei gegenteiliger Beobachtung: Hypothese als `refutes` oder `inconclusive` einstufen.

## Variablen

| Variable              | Beschreibung                    | Kontrolle / Treatment |
| --------------------- | ------------------------------- | --------------------- |
| artifact_class_policy | Klassentrennung im Contract     | vorher / nachher      |
| ci_semantics          | Blocking vs non-blocking split  | vorher / nachher      |
| pr_type               | Art der geaenderten PR          | gemischt / gemischt   |
| reviewer_context      | Review-Erfahrung mit neuem Setup| begrenzt / zunehmend  |

## Risiken und Einschränkungen

- Geringe Stichprobe kann Zufallseffekte ueberbetonen.
- Baseline-PRs sind evtl. nicht voll vergleichbar.
- Subjektive Metriken muessen klar von beobachteten Metriken getrennt bleiben.
