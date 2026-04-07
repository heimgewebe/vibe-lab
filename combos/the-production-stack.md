---
name: "The Production Stack"
style: spec-first-vibe
techniques: [chain-of-thought, context-stuffing, prompt-chaining]
tools: [cursor]
difficulty: intermediate
best_for: [production-apis, backend-services, full-stack-apps]
ratings:
  speed: 3
  accuracy: 5
  code_quality: 5
  iterability: 4
  cognitive_load: 3
  scalability: 4
  creativity: 2
tags: [production, quality, systematic, backend]
---

# 🏗️ The Production Stack

**Stil**: Spec-First Vibe | **Techniken**: Chain-of-Thought + Context Stuffing + Prompt Chaining | **Tool**: Cursor

## Beschreibung

Die Kombination für **produktionsreifen Code**: Zuerst spezifizieren, dann durchdenken, dann schrittweise umsetzen – alles mit maximalem Kontext zum bestehenden Projekt.

## Rezept

### Schritt 1: Spec erstellen (Spec-First)
```
"Erstelle eine technische Spezifikation für [Feature].
Beachte unsere bestehende Architektur: @architecture.md
Und unsere Code-Konventionen: @.cursorrules"
```

### Schritt 2: Architektur durchdenken (Chain-of-Thought)
```
"Denke Schritt für Schritt:
1. Welche bestehenden Komponenten sind betroffen?
2. Welche neuen Komponenten werden benötigt?
3. Welche Datenmodell-Änderungen sind nötig?
4. Welche Edge Cases müssen berücksichtigt werden?"
```

### Schritt 3: Schrittweise implementieren (Prompt Chaining)
```
Chain 1: "Erstelle das Datenmodell basierend auf der Spec."
Chain 2: "Implementiere die Service-Layer-Logik."
Chain 3: "Erstelle die API-Endpoints."
Chain 4: "Schreibe Tests für alle Komponenten."
```

## Erfahrungsbericht

- **Zeitaufwand**: ~2x langsamer als YOLO, aber ~3x weniger Rework
- **Qualität**: Konsistent hoch, wenige Bugs
- **Geeignet für**: Teams, Code-Reviews, langlebige Projekte

## Wann NICHT verwenden

- Für Prototypen oder MVPs (zu langsam)
- Für triviale Aufgaben (Overhead zu hoch)
- Wenn die Anforderungen noch unklar sind
