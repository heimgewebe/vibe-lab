---
title: "Failure Modes — Incremental Refinement"
status: inconclusive
canonicality: operative
---

# Failure Modes — Incremental Refinement

## Wann funktioniert diese Praxis NICHT?

- [ ] Bei sehr einfachen Tasks (< 20 Zeilen), wo die Zerlegung mehr Overhead als Nutzen bringt
- [ ] Wenn das LLM bei späteren Schritten den Kontext aus früheren Schritten verliert (Context Window Overflow)
- [ ] Wenn die Teilschritte schlecht gewählt sind und zu inkohärenten Zwischenzuständen führen
- [ ] Wenn die Zerlegung semantische Fehler zwischen Modulen einführt, die der Typchecker nicht erkennt (siehe Task-2-Bug)

## Bekannte Fehlannahmen

- [ ] Annahme, dass die Zerlegung in Teilschritte objektiv und reproduzierbar ist — sie hängt stark von der Erfahrung des Prompters ab
- [ ] Annahme, dass mehr Prompts automatisch bessere Ergebnisse liefern — es gibt vermutlich einen Punkt abnehmenden Grenznutzens
- [ ] Annahme, dass Modularität Korrektheit impliziert — mehr Dateien und Typen bedeuten nicht automatisch weniger Bugs
- [ ] Annahme, dass Kompilierung Qualität belegt — Typkorrektheit ≠ Laufzeitkorrektheit
- [ ] Annahme, dass Testbarkeit (durch Exports) gleich Getestetheit ist — ohne tatsächliche Tests bleibt der Vorteil theoretisch

## Grenzen der Evidenz

- Stichprobengröße: 3 Tasks pro Variante — zu klein für belastbare statistische Aussagen
- Kontext-Abhängigkeit: Nur TypeScript/Node.js getestet; andere Sprachen und Frameworks könnten anders reagieren
- Selbst-Selektion: Der Experimentator wählt die Zerlegung — eine andere Zerlegung könnte andere Ergebnisse liefern
- Experimentator-Bias: Derselbe Agent erzeugte beide Arme; Incremental bekommt systematisch mehr Bearbeitungszeit und Strukturzwang
- Proxy-Metriken: Dateien, Typen, Error-Handling-Konstrukte messen Modularität, nicht Korrektheit oder Wartbarkeit
- Fehlende Runtime-Evidenz: Kein Code wurde ausgeführt; kein Laufzeittest, keine Smoke-Tests
- Fehlende Tests: method.md definiert „Tests generieren" als Schritt 6, aber keine Testdateien vorhanden
- Rework nur geschätzt: Keine gemessenen Patch-Diffs oder Nacharbeits-Zeilen

## Im Experiment aufgetretene Fehler

- **Task 2 CLI-Parser-Bug:** Doppeltes `i++` in allen switch-cases des Argument-Parsers führt dazu, dass nach jedem Flag mit Wert das nächste Argument übersprungen wird. Kompiliert fehlerfrei, versagt zur Laufzeit. Exemplarisch für: Modularität schützt nicht vor semantischen Fehlern.

## Risiko einer Fehlanwendung

Incremental Refinement könnte zur Überstrukturierung verleiten: Jeder Mini-Prompt wird zum Ritual, statt bedarfsgerecht zwischen Single-Shot und Incremental zu wählen. Die Praxis funktioniert am besten als bewusste Entscheidung, nicht als Default.

Zusätzliches Risiko: Teams ritualisieren 6-teilige Promptketten auch dort, wo 1 guter Prompt reicht — mehr formale Ordnung, aber nicht zwingend mehr Outcome.
