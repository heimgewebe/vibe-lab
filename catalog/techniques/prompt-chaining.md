---
name: "Prompt Chaining"
category: technique
maturity: proven
tools: [cursor, claude-code, chatgpt, aider]
synergies: [incremental-refinement, spec-first-vibe, chain-of-thought]
anti-synergies: [yolo-prompting]
complexity: medium
speed_boost: "3x"
quality_impact: "++"
tags: [prompting, multi-step, workflow, systematic]
last_tested: 2026-04-01
---

# 🔗 Prompt Chaining

## Beschreibung

Prompt Chaining zerlegt eine komplexe Aufgabe in eine **Kette von aufeinander aufbauenden Prompts**. Jeder Prompt nutzt den Output des vorherigen als Input – wie eine Pipeline.

## Wie es funktioniert

1. **Aufgabe zerlegen**: In logische, aufeinander aufbauende Schritte
2. **Prompt 1**: Erster Schritt → Output 1
3. **Prompt 2**: Output 1 als Input → Output 2
4. **Prompt N**: Output N-1 als Input → Endergebnis

## Beispiel: API-Entwicklung

```
Prompt 1 (Analyse):
"Analysiere diese Anforderungen und erstelle eine Liste aller 
benötigten API-Endpoints mit HTTP-Method, Path, Request/Response-Body."

Prompt 2 (Datenmodell):
"Basierend auf diesen Endpoints: [Output 1]
Erstelle das Datenmodell mit allen Entitäten und Beziehungen."

Prompt 3 (Implementation):
"Basierend auf dem Datenmodell: [Output 2]
Implementiere die API-Endpoints mit Express und Prisma."

Prompt 4 (Tests):
"Basierend auf der Implementation: [Output 3]
Schreibe Tests für alle Endpoints."
```

## Wann einsetzen?

- ✅ Komplexe, mehrstufige Aufgaben
- ✅ Wenn jeder Schritt vom vorherigen abhängt
- ✅ Für reproduzierbare Workflows
- ✅ Wenn Zwischenergebnisse validiert werden sollen
- ❌ Einfache, einmalige Aufgaben
- ❌ Wenn Geschwindigkeit wichtiger als Qualität ist

## Bewertung

| Dimension | Score | Kommentar |
|-----------|:-----:|-----------|
| ⏱️ Geschwindigkeit | 3/5 | Mehr Prompts, aber weniger Rework |
| 🎯 Treffsicherheit | 4/5 | Jeder Schritt kann validiert werden |
| 🏗️ Codequalität | 4/5 | Durchdachte Schritte → besserer Code |
| 🔄 Iterationsfähigkeit | 5/5 | Man kann bei jedem Schritt eingreifen |
| 🧠 Kognitive Last | 3/5 | Chain-Design erfordert Planung |
| 📐 Skalierbarkeit | 4/5 | Gut für große Aufgaben |
| 🎨 Kreativität | 3/5 | Struktur kann Kreativität einschränken |
