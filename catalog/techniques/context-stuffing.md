---
name: "Context Stuffing"
category: technique
maturity: proven
tools: [cursor, claude-code, aider, chatgpt]
synergies: [spec-first-vibe, architecture-first-vibe, full-auto-generation]
anti-synergies: []
complexity: medium
speed_boost: "2x"
quality_impact: "++"
tags: [context, prompting, quality, advanced]
last_tested: 2026-04-01
---

# 📦 Context Stuffing

## Beschreibung

Context Stuffing ist die Technik, dem KI-Modell **so viel relevanten Kontext wie möglich** mitzugeben – bestehender Code, Dokumentation, Beispiele, Konventionen – damit die generierte Lösung optimal zum Projekt passt.

## Wie es funktioniert

1. **Relevanten Kontext identifizieren**: Welche Informationen braucht die KI?
2. **Kontext bereitstellen**: Code, Docs, Beispiele in den Prompt laden
3. **Aufgabe formulieren**: Was soll die KI damit tun?

## Beispiel

```
"Hier ist unser bestehender User-Service:
[bestehender Code]

Hier sind unsere Code-Konventionen:
[Konventionen]

Hier ist ein Beispiel eines ähnlichen Services:
[Beispiel]

Erstelle nun einen neuen Product-Service, der den gleichen 
Patterns und Konventionen folgt."
```

## Arten von Kontext

| Art | Beispiel | Wirkung |
|-----|---------|---------|
| **Code-Kontext** | Bestehende Dateien, Interfaces | Konsistente Patterns |
| **Style-Kontext** | Linter-Config, Code-Conventions | Einheitlicher Stil |
| **Domain-Kontext** | Fachbegriffe, Business-Regeln | Korrekte Semantik |
| **Architektur-Kontext** | System-Diagramme, README | Passende Struktur |
| **Beispiel-Kontext** | Ähnliche Implementierungen | Template für Output |

## Tools & Features

- **Cursor**: `@`-Referenzen auf Dateien, Docs, Symbole
- **Cursor**: `.cursorrules` für projektweite Konventionen
- **Claude Code**: `CLAUDE.md` für Projektkontext
- **Aider**: Dateien zum Chat hinzufügen
- **ChatGPT**: Manuelles Copy-Paste von Kontext

## Wann einsetzen?

- ✅ In bestehenden Projekten (Brownfield)
- ✅ Wenn Konsistenz wichtig ist
- ✅ Bei projektspezifischen Konventionen
- ✅ Für Team-Projekte mit Code-Standards
- ❌ Bei Greenfield ohne bestehenden Code
- ❌ Wenn der Kontext das Kontextfenster überschreitet

## Bewertung

| Dimension | Score | Kommentar |
|-----------|:-----:|-----------|
| ⏱️ Geschwindigkeit | 3/5 | Kontext-Sammlung braucht Zeit |
| 🎯 Treffsicherheit | 5/5 | Mehr Kontext = bessere Ergebnisse |
| 🏗️ Codequalität | 5/5 | Konsistenter Code durch Kontext |
| 🔄 Iterationsfähigkeit | 4/5 | Kontext muss nur einmal gesetzt werden |
| 🧠 Kognitive Last | 3/5 | Kontext-Auswahl erfordert Nachdenken |
| 📐 Skalierbarkeit | 3/5 | Limitiert durch Kontextfenstergröße |
| 🎨 Kreativität | 2/5 | Kontext schränkt Lösungsraum ein |
