---
name: "Rubber-Duck-Prompting"
category: technique
maturity: proven
tools: [cursor, claude-code, copilot, chatgpt, aider]
synergies: [pair-programming-mit-ki, chain-of-thought]
anti-synergies: []
complexity: low
speed_boost: "2x"
quality_impact: "+"
tags: [prompting, debugging, problem-solving, universal, beginner-friendly]
last_tested: 2026-04-01
---

# 🦆 Rubber-Duck-Prompting

## Beschreibung

Rubber-Duck-Prompting nutzt die KI als **intelligente Gummiente**: Man erklärt sein Problem oder seine Idee der KI, und allein durch das Formulieren – plus die KI-Antwort – kommen bessere Lösungen zustande als durch direktes Prompting.

## Wie es funktioniert

1. **Problem beschreiben**: Erkläre der KI was du erreichen willst
2. **Kontext teilen**: Was hast du schon versucht? Was funktioniert nicht?
3. **Dialog führen**: Lass die KI Rückfragen stellen
4. **Gemeinsam lösen**: Aus dem Dialog entsteht die Lösung

## Beispiel

```
"Ich versuche eine Caching-Schicht für unsere API zu bauen. 
Wir haben Express mit PostgreSQL. Das Problem: Manche Endpoints 
ändern sich oft, andere selten. Ich bin unsicher, ob ich Redis, 
in-memory Caching oder einen HTTP-Cache-Header-Ansatz nehmen soll.

Was würdest du empfehlen? Welche Fragen müssen wir zuerst klären?"
```

## Varianten

### Problem-Exploration
```
"Ich habe ein Performance-Problem. Lass mich dir beschreiben was passiert..."
```

### Architecture-Rubber-Duck
```
"Ich überlege ob wir Microservices oder Monolith nehmen sollen. 
Lass uns das gemeinsam durchdenken..."
```

### Code-Review-Rubber-Duck
```
"Schau dir diesen Code an. Ich habe ein ungutes Gefühl dabei.
Was könnte hier besser sein?"
```

## Wann einsetzen?

- ✅ Wenn man nicht weiß, wo man anfangen soll
- ✅ Bei Architekturentscheidungen
- ✅ Zum Debugging schwer fassbarer Probleme
- ✅ Wenn man eine zweite Meinung braucht
- ❌ Wenn die Aufgabe klar definiert ist
- ❌ Für reine Code-Generierung

## Bewertung

| Dimension | Score | Kommentar |
|-----------|:-----:|-----------|
| ⏱️ Geschwindigkeit | 2/5 | Dialog braucht Zeit |
| 🎯 Treffsicherheit | 4/5 | Durchdachte Lösungen |
| 🏗️ Codequalität | 4/5 | Gründliches Durchdenken → besserer Code |
| 🔄 Iterationsfähigkeit | 5/5 | Dialog ist natürlich iterativ |
| 🧠 Kognitive Last | 5/5 | KI hilft beim Denken |
| 📐 Skalierbarkeit | 4/5 | Auch für komplexe Probleme |
| 🎨 Kreativität | 5/5 | Dialog erzeugt neue Ideen |
