---
title: "Failure Modes: Pre-Mortem Prompting"
status: testing
canonicality: operative
document_role: experiment
---

# Failure Modes — Pre-Mortem Prompting

## Wann funktioniert diese Praxis NICHT?

- Wenn Fehlräume außerhalb der antizipierten Ontologie liegen.
- Wenn neue exotische Wertbereiche (z. B. micro_price) nicht explizit modelliert werden.

## Neue Regelkategorien (aus Run 014/015)

- **Low-/Micro-Price-Klasse:** Preise nahe 0 müssen explizit als potenziell ungültig behandelt werden.
- **Range-Bounds-Klasse:** Preis- und Mengenbereiche brauchen obere/untere Grenzen, nicht nur Typchecks.
- **Structure-Klasse:** `items` muss Liste von Objekten sein; null/falscher Typ sind harte Fehler.

## Grenzen der Evidenz

- Eine Challenge-Familie dominiert.
- Replikation bislang nur Session-B innerhalb derselben Modellfamilie.
- Keine Cross-Model-Replikation.

## Risiko einer Fehlanwendung

Pre-Mortem kann Scheinsicherheit erzeugen, wenn es nur bekannte Fehlpfade abdeckt und exotische Klassen ausblendet.
