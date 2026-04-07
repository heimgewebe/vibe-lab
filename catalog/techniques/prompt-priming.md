---
name: "Prompt Priming"
category: technique
maturity: proven
tools: [cursor, claude-code, copilot, chatgpt, aider, windsurf]
synergies: [context-stuffing, spec-first-vibe, guided-yolo]
anti-synergies: []
complexity: low
speed_boost: "2x"
quality_impact: "++"
tags: [prompting, quality, universal, beginner-friendly, system-prompt]
last_tested: 2026-04-01
---

# 🎬 Prompt Priming

## Beschreibung

Prompt Priming gibt der KI **vorab eine Rolle, Persönlichkeit oder Perspektive**, bevor die eigentliche Aufgabe gestellt wird. Die KI "schlüpft in eine Rolle" und generiert entsprechend qualitativeren Output.

## Wie es funktioniert

1. **Rolle definieren**: Wer soll die KI sein?
2. **Kontext setzen**: In welcher Situation befindet sie sich?
3. **Aufgabe stellen**: Was soll sie tun?

## Beispiele

### Senior Developer
```
"Du bist ein Senior TypeScript-Entwickler mit 15 Jahren Erfahrung.
Du schreibst sauberen, gut getesteten Code und bevorzugst 
funktionale Patterns. Du erklärst deine Entscheidungen.

Aufgabe: Implementiere einen Cache-Invalidation-Service."
```

### Code Reviewer
```
"Du bist ein strenger Code-Reviewer bei einem FAANG-Unternehmen.
Du achtest besonders auf: Security, Performance, Wartbarkeit.
Du gibst konkretes, actionable Feedback.

Reviewe diesen Pull Request: [Code]"
```

### Architektur-Berater
```
"Du bist ein Cloud-Architekt mit Spezialisierung auf 
Distributed Systems. Du denkst in Trade-offs und erklärst 
Vor- und Nachteile jeder Entscheidung.

Entwirf die Architektur für: [Anforderung]"
```

## Wann einsetzen?

- ✅ Immer – Priming verbessert fast jedes Ergebnis
- ✅ Besonders bei spezialisierten Aufgaben
- ✅ Wenn bestimmte Qualitätsnormen eingehalten werden sollen
- ✅ In System-Prompts und `.cursorrules`
- ❌ Für triviale Autocomplete-Aufgaben

## Bewertung

| Dimension | Score | Kommentar |
|-----------|:-----:|-----------|
| ⏱️ Geschwindigkeit | 4/5 | Minimaler Overhead, großer Effekt |
| 🎯 Treffsicherheit | 4/5 | Rolle fokussiert den Output |
| 🏗️ Codequalität | 4/5 | "Senior Developer" → besserer Code |
| 🔄 Iterationsfähigkeit | 4/5 | Rolle bleibt über Iterationen |
| 🧠 Kognitive Last | 5/5 | Einfach anzuwenden |
| 📐 Skalierbarkeit | 4/5 | Funktioniert bei jeder Projektgröße |
| 🎨 Kreativität | 4/5 | Verschiedene Rollen → verschiedene Perspektiven |
