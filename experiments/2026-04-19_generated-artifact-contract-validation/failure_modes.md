---
title: "Failure Modes: Generated Artifact Contract Validation"
status: draft
canonicality: operative
---

# Failure Modes — Generated Artifact Contract Validation

<!-- Pflichtbestandteil ab Status: testing. Muss vor Promotion ausgefüllt sein. -->
<!-- Constraint: failure-modes-required (.vibe/constraints.yml) -->

## Wann funktioniert diese Praxis NICHT?

<!-- Konkrete Bedingungen, unter denen der Ansatz versagt oder kontraproduktiv ist. -->

- [ ] Contract-Klassen sind falsch zugeordnet, sodass echte Risiken non-blocking werden.
- [ ] Canonical-Dateien werden ausserhalb der vorgesehenen Generatorpfade veraendert.

## Bekannte Fehlannahmen

<!-- Welche Voraussetzungen wurden beim Experiment getroffen, die in der Realität möglicherweise nicht gelten? -->

- [ ] Baseline und neue PRs seien direkt vergleichbar, obwohl Scope und Komplexitaet differieren.
- [ ] Weniger blockierende Fehler bedeuten automatisch bessere Qualitaet.

## Grenzen der Evidenz

<!-- Was kann aus den erhobenen Daten NICHT geschlossen werden? -->

- Stichprobengröße: <!-- Wie viele Tasks / Iterationen? Reicht das? -->
- Kontext-Abhängigkeit: <!-- In welchen Kontexten wurde NICHT getestet? -->
- Selbst-Selektion: <!-- Welche Verzerrungen können vorliegen? -->

## Risiko einer Fehlanwendung

<!-- Was passiert, wenn diese Praxis blind angewendet wird, ohne die Grenzen zu kennen? -->

<!-- Beispiel: -->
<!-- "Spec-First kann überspezifizieren und Exploration blockieren, wenn die Domäne noch
     nicht verstanden ist." -->

Ein blinder Fokus auf "weniger rote CI" kann dazu fuehren, dass relevante Drift in falschen Klassen verschwindet und damit spaeter teurer wird.
