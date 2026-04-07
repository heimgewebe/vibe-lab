---
name: "Context Window Overflow"
category: anti-pattern
maturity: proven
tools: [cursor, claude-code, copilot, chatgpt, aider]
synergies: []
anti-synergies: []
complexity: low
speed_boost: "-1x"
quality_impact: "---"
tags: [anti-pattern, context, quality, universal]
last_tested: 2026-04-01
---

# 🚫 Context Window Overflow

## Was ist es?

Dem KI-Modell **zu viel Kontext** auf einmal geben, sodass das Kontextfenster überläuft und die Qualität des Outputs dramatisch sinkt. Die KI "vergisst" wichtige Details oder halluziniert.

## Symptome

- KI "vergisst" Anforderungen, die früh im Gespräch gestellt wurden
- Output widerspricht sich selbst
- Generierter Code referenziert nicht existierende Funktionen
- Qualität des Outputs nimmt im Gesprächsverlauf ab
- KI wiederholt sich oder dreht sich im Kreis

## Warum passiert es?

- **Zu langes Gespräch** – der Kontext wächst mit jedem Exchange
- **Zu viele Dateien** auf einmal referenziert
- **Redundanter Kontext** – gleiche Informationen mehrfach
- **Irrelevanter Kontext** – Informationen, die für die Aufgabe nicht nötig sind

## Wie vermeiden?

### ✅ Neue Konversation starten
Wenn ein Gespräch zu lang wird, besser eine neue Konversation mit frischem Kontext starten.

### ✅ Kontext priorisieren
Nur die relevantesten Dateien und Informationen bereitstellen.

### ✅ Zusammenfassen
Statt die gesamte History zu behalten, eine Zusammenfassung des bisherigen Stands geben.

### ✅ Aufgaben aufteilen
Große Aufgaben in kleinere, unabhängige Teilaufgaben zerlegen.

## Beispiel

### ❌ Schlecht
```
"Hier sind alle 47 Dateien meines Projekts. 
Bitte erstelle ein neues Feature das..."
[47 Dateien mit insgesamt 10.000 Zeilen]
```

### ✅ Besser
```
"Hier sind die 3 relevanten Dateien für das neue Feature:
- user.model.ts (Datenmodell)
- auth.service.ts (wird erweitert)
- auth.controller.ts (neuer Endpoint)

Erstelle basierend auf diesen einen neuen /auth/mfa Endpoint."
```

## Schweregrad: 🔴 Hoch

Dieses Anti-Pattern ist einer der häufigsten Gründe für schlechte Vibe-Coding-Ergebnisse.
