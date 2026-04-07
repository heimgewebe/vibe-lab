---
name: "Cursor"
category: technology
maturity: proven
tools: [cursor]
synergies: [pair-programming-mit-ki, full-auto-generation, spec-first-vibe]
anti-synergies: []
complexity: medium
speed_boost: "5x"
quality_impact: "+"
tags: [ide, editor, ai-native, vscode, composer, agent]
last_tested: 2026-04-01
---

# 💻 Cursor

## Beschreibung

Cursor ist eine **KI-native IDE** basierend auf VS Code, die AI-Assistenz tief in den Entwicklungsworkflow integriert. Mit Features wie Composer, Chat, und Inline-Edit ist es eines der leistungsstärksten Vibe-Coding-Tools.

## Kernfeatures

### Composer (Multi-File Generation)
- Kann mehrere Dateien gleichzeitig erstellen und bearbeiten
- Ideal für Full-Auto Generation und Spec-First Vibe
- Versteht Projektkontext über Dateigrenzen hinweg

### Chat (Inline-Konversation)
- Direkter Dialog mit der KI im Editor
- Codebase-Awareness: versteht den gesamten Projektkontext
- Kann referenzierte Dateien, Docs und Symbole verstehen

### Tab-Autocomplete
- KI-gesteuerte Autocomplete über mehrere Zeilen
- Ideal für Pair-Programming-Stil
- Lernt den Codestil im Projekt

### Inline Edit (Cmd+K)
- Schnelle, gezielte Änderungen im Code
- Selektiere Code → beschreibe Änderung → fertig

## Stärken

- **Tiefste IDE-Integration** – KI ist kein Plugin, sondern Kernfeature
- **Multi-Model Support** – Claude, GPT-4, eigene Modelle
- **Codebase-Awareness** – versteht das gesamte Projekt
- **Composer** – Multi-File-Generierung ist einzigartig
- **VS Code kompatibel** – alle Extensions funktionieren

## Schwächen

- **Kostenpflichtig** – Pro-Plan nötig für volle Funktionalität
- **Closed Source** – keine vollständige Transparenz
- **Modell-Abhängigkeit** – Qualität hängt vom gewählten Modell ab
- **Lernkurve** – viele Features brauchen Einarbeitung

## Best Practices

1. **`.cursorrules` nutzen** – Projektspezifische KI-Anweisungen definieren
2. **Kontext gezielt setzen** – relevante Dateien mit @ referenzieren
3. **Composer für Multi-File** – nicht für einzelne kleine Änderungen
4. **Tab-Complete trainieren** – durch konsistenten Codestil

## Kompatibilität mit Vibe-Stilen

| Stil | Kompatibilität | Feature |
|------|:--------------:|---------|
| YOLO-Prompting | ⭐⭐⭐⭐⭐ | Chat + Composer |
| Spec-First Vibe | ⭐⭐⭐⭐ | Composer + Docs |
| TDD-Vibe | ⭐⭐⭐⭐ | Inline Edit |
| Pair-Programming | ⭐⭐⭐⭐⭐ | Tab-Complete + Chat |
| Full-Auto Generation | ⭐⭐⭐⭐⭐ | Composer |
| Incremental Refinement | ⭐⭐⭐⭐ | Chat + Inline Edit |
