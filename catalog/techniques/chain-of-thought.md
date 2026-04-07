---
name: "Chain-of-Thought Prompting"
category: technique
maturity: proven
tools: [cursor, claude-code, copilot, chatgpt, aider]
synergies: [spec-first-vibe, tdd-vibe, incremental-refinement]
anti-synergies: [yolo-prompting]
complexity: low
speed_boost: "2x"
quality_impact: "++"
tags: [prompting, reasoning, quality, universal]
last_tested: 2026-04-01
---

# 🧠 Chain-of-Thought Prompting

## Beschreibung

Chain-of-Thought (CoT) Prompting fordert die KI auf, **Schritt für Schritt zu denken**, bevor sie Code generiert. Statt direkt zum Output zu springen, durchläuft die KI einen expliziten Denkprozess.

## Wie es funktioniert

1. **Problem beschreiben**
2. **"Denke Schritt für Schritt"** – die magische Formel
3. **KI legt Denkprozess offen** – Analyse, Optionen, Entscheidung
4. **Dann erst Implementation**

## Beispiel

```
"Ich brauche eine Funktion, die den kürzesten Weg in einem 
gewichteten Graphen findet.

Denke Schritt für Schritt:
1. Welche Algorithmen kommen in Frage?
2. Welcher ist für meinen Use Case am besten?
3. Welche Datenstrukturen brauche ich?
4. Dann implementiere die Lösung."
```

## Varianten

### Explicit CoT
```
"Erkläre mir zuerst deinen Ansatz, dann implementiere."
```

### Structured CoT
```
"Analysiere die Aufgabe in diesen Schritten:
1. Anforderungen identifizieren
2. Edge Cases auflisten
3. Algorithmus wählen
4. Implementieren
5. Tests schreiben"
```

### Comparative CoT
```
"Vergleiche drei mögliche Ansätze, wähle den besten, und implementiere ihn."
```

## Wann einsetzen?

- ✅ Komplexe algorithmische Probleme
- ✅ Architekturentscheidungen
- ✅ Wenn man den Denkprozess verstehen will
- ✅ Sicherheitskritische Implementierungen
- ❌ Einfache, triviale Aufgaben
- ❌ Wenn Geschwindigkeit wichtiger als Verständnis ist

## Bewertung

| Dimension | Score | Kommentar |
|-----------|:-----:|-----------|
| ⏱️ Geschwindigkeit | 3/5 | Langsamer durch Denkprozess |
| 🎯 Treffsicherheit | 4/5 | Durchdachte Lösungen sind öfter richtig |
| 🏗️ Codequalität | 4/5 | Reasoning führt zu besseren Entscheidungen |
| 🔄 Iterationsfähigkeit | 4/5 | Man kann am Denkprozess ansetzen |
| 🧠 Kognitive Last | 4/5 | KI erklärt ihr Denken → weniger eigenes Denken |
| 📐 Skalierbarkeit | 4/5 | Skaliert gut für komplexe Probleme |
| 🎨 Kreativität | 3/5 | Strukturiertes Denken kann Kreativität einschränken |
