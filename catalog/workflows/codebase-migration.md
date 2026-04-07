---
name: "Codebase Migration Workflow"
category: workflow
maturity: experimental
tools: [cursor, claude-code, aider]
synergies: [incremental-refinement, context-stuffing, chain-of-thought]
anti-synergies: [yolo-prompting, full-auto-generation]
complexity: high
speed_boost: "3x"
quality_impact: "++"
tags: [migration, refactoring, legacy, workflow, systematic]
last_tested: 2026-04-01
---

# 🔄 Codebase Migration Workflow

## Beschreibung

Ein systematischer Workflow für die KI-gestützte Migration bestehenden Codes – ob Sprache, Framework, Architektur oder Technologie.

## Der Workflow

### Phase 1: Analyse (30 Min)

```
"Analysiere diese Codebase:
[relevante Dateien referenzieren]

1. Welche Komponenten und Module gibt es?
2. Wie sind die Abhängigkeiten?
3. Welche Patterns werden verwendet?
4. Welche Tests existieren?"
```

### Phase 2: Migrationsstrategie (30 Min)

```
"Ich möchte von [ALT] zu [NEU] migrieren.

Erstelle eine Migrationsstrategie:
1. Reihenfolge der zu migrierenden Komponenten (Abhängigkeiten beachten!)
2. Welche Komponenten können 1:1 übersetzt werden?
3. Welche brauchen Neudesign?
4. Wie stelle ich sicher, dass bestehende Funktionalität erhalten bleibt?"
```

### Phase 3: Inkrementelle Migration (iterativ)

```
"Migriere [Komponente X] von [ALT] zu [NEU].
Beachte:
- Bestehende Tests müssen weiter bestehen
- Die Schnittstelle zur restlichen Codebase bleibt kompatibel
- Gleiche Patterns wie in bereits migrierten Komponenten verwenden"
```

### Phase 4: Validierung

```
"Alle Komponenten sind migriert. Bitte:
1. Prüfe ob alle Tests bestehen
2. Identifiziere verbleibende Referenzen auf den alten Code
3. Prüfe Konsistenz der neuen Codebase
4. Erstelle eine Zusammenfassung der Änderungen"
```

## Bewertung

| Dimension | Score | Kommentar |
|-----------|:-----:|-----------|
| ⏱️ Geschwindigkeit | 4/5 | Deutlich schneller als manuelle Migration |
| 🎯 Treffsicherheit | 3/5 | Jeder Schritt muss validiert werden |
| 🏗️ Codequalität | 4/5 | Systematischer Ansatz erhält Qualität |
| 🔄 Iterationsfähigkeit | 5/5 | Inkrementell by Design |
| 🧠 Kognitive Last | 3/5 | Strategie-Planung erfordert Nachdenken |
| 📐 Skalierbarkeit | 4/5 | Auch für große Codebases |
| 🎨 Kreativität | 2/5 | Migration ist eher mechanisch |
