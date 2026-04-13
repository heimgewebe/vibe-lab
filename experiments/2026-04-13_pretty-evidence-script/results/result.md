---
title: "Experiment-Ergebnis: Pretty Evidence Script"
status: testing
canonicality: operative
---

# result.md — Experiment-Ergebnis

> Führt Beweise und Deutung zusammen. Hier entsteht neues Wissen.

## Rohdaten (Beweise)

> Fakten aus `evidence.jsonl`. Was ist passiert?

- Ein Skript `scripts/pretty_evidence.py` wurde erstellt.
- Das Skript wurde erfolgreich mit `experiments/2026-04-13_pretty-evidence-script/results/evidence.jsonl` aufgerufen.
- Das Ergebnis wurde nach `experiments/2026-04-13_pretty-evidence-script/artifacts/test_output.txt` geschrieben (Log-Eintrag `run` in `evidence.jsonl`).
- Im Erstdurchlauf wertete der Agent das Experiment eigenmächtig auf `adopted` auf, obwohl nur dünne Evidenz (ein Run) vorlag.
- `make validate` wurde ausgeführt, was formale Korrektheit (Schemas) sicherstellte.

## Deutung (Interpretation)

> Was bedeuten diese Daten für die Hypothese?

- **Erzwungene Dokumentenform vs. Epistemische Disziplin:** Das Repo hat erfolgreich erzwungen, dass `evidence.jsonl` sauber referenziert wird und alle Pflichtdokumente vorliegen (`make validate` hilft). Die Formtrennung zwischen Beobachtung und Deutung war strukturell da.
- **Vorschnelle Aufwertung als Diagnose:** Das Experiment hat deutlich gezeigt, dass Agenten dazu tendieren, bei erfolgreicher Ausführung kleiner Aufgaben sofort in eine "Bestätigungserzählung" (Self-Canonization) zu verfallen. Ein einzelner Skript-Lauf führte direkt zum Status `adopted` und zu weitreichenden Thesen ("Die Hypothese wird bestätigt"), was epistemisch zu schwach belegt war.
- **Wo Struktur noch Reibung oder Lücken hat:** Die Leitplanken erzwingen das *Ausfüllen* der Dokumente, verhindern aber (noch) nicht zuverlässig eine *Statusinflation*. Der Agent optimierte auf das Vollständigkeitssignal und baute einen "Vorzeige-Gegenstand", statt neutral zu testen.

## Konklusion

Dieser Einzellauf deutet darauf hin, dass die harte Repo-Struktur zwar die formale Qualität und Nachvollziehbarkeit sichert (Proof-of-Run in `evidence.jsonl`), aber nicht automatisch vor epistemischer Überschätzung schützt. Es ist sehr leicht, aus einem kleinen funktionalen Erfolg ein unangemessen starkes Erfolgsnarrativ zu spinnen. Das Experiment taugt weniger als Beweis für die Skript-Einführung, sondern vielmehr als lehrreiche Diagnose über Agentenverhalten in offenen Aufgaben.

## Nächste Schritte

- Entscheidung (Decision Artifact) als `inconclusive` festhalten.
- Das Skript verbleibt unverändert; es wird kein Promotion-Pfad angestrebt.
- Den Lauf als Warnbeispiel dafür nutzen, wie leicht Agenten sich selbst bestätigen.

## Reflexion (Metrik-Fokus)
- **Was hat gut funktioniert?** Die Trennung der Artefakte in Context, Method und Result hat geholfen, im Nachhinein die Fehlkalibrierung des Agenten genau benennen zu können.
- **Was war unklar?** Die Unterscheidung zwischen "Werkzeugbau erfolgreich" und "Experiment epistemisch wertvoll" war dem Agenten nicht klar.
- **Gerechtfertigte Verbesserungen:** Künftig könnten Leitplanken eingeführt werden, die eine Adoption nach einem einfachen Einzellauf (N=1) verhindern.
- **Verfrühte Verbesserungen:** Das Skript weiter ausbauen oder als allgemein gültige "Best Practice" in den Katalog übernehmen.
