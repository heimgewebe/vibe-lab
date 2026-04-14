---
title: "Failure Modes — Incremental Refinement"
status: designed
canonicality: operative
---

# Failure Modes — Incremental Refinement

## Wann funktioniert diese Praxis NICHT?

- [ ] Bei sehr einfachen Tasks (< 20 Zeilen), wo die Zerlegung mehr Overhead als Nutzen bringt
- [ ] Wenn das LLM bei späteren Schritten den Kontext aus früheren Schritten verliert (Context Window Overflow)
- [ ] Wenn die Teilschritte schlecht gewählt sind und zu inkohärenten Zwischenzuständen führen

## Bekannte Fehlannahmen

- [ ] Annahme, dass die Zerlegung in Teilschritte objektiv und reproduzierbar ist — sie hängt stark von der Erfahrung des Prompters ab
- [ ] Annahme, dass mehr Prompts automatisch bessere Ergebnisse liefern — es gibt vermutlich einen Punkt abnehmenden Grenznutzens

## Grenzen der Evidenz

- Stichprobengröße: 3 Tasks pro Variante — zu klein für belastbare statistische Aussagen
- Kontext-Abhängigkeit: Nur TypeScript/Node.js getestet; andere Sprachen und Frameworks könnten anders reagieren
- Selbst-Selektion: Der Experimentator wählt die Zerlegung — eine andere Zerlegung könnte andere Ergebnisse liefern

## Risiko einer Fehlanwendung

Incremental Refinement könnte zur Überstrukturierung verleiten: Jeder Mini-Prompt wird zum Ritual, statt bedarfsgerecht zwischen Single-Shot und Incremental zu wählen. Die Praxis funktioniert am besten als bewusste Entscheidung, nicht als Default.
