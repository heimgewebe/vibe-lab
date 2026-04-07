---
name: "Prompt Vagueness"
category: anti-pattern
maturity: proven
tools: [cursor, claude-code, copilot, chatgpt, aider]
synergies: []
anti-synergies: []
complexity: low
speed_boost: "-1x"
quality_impact: "--"
tags: [anti-pattern, prompting, quality, universal]
last_tested: 2026-04-01
---

# 🚫 Prompt Vagueness

## Was ist es?

Zu vage, unspezifische Prompts verwenden und sich dann wundern, dass die Ergebnisse nicht passen. **Garbage In → Garbage Out** gilt auch für Vibe-Coding.

## Symptome

- "Das ist nicht was ich gemeint habe" – ständig
- Endlose Iteration, weil die KI nie das Richtige trifft
- Output ist technisch korrekt, aber am Ziel vorbei
- Frustration und Vertrauensverlust in KI-Tools

## Beispiele

### ❌ Vage
```
"Mach mir eine Datenbank"
"Baue ein Login"
"Verbessere den Code"
```

### ✅ Spezifisch
```
"Erstelle ein PostgreSQL-Schema mit Prisma für eine User-Tabelle 
mit id (UUID), email (unique), password_hash, created_at, updated_at"

"Implementiere JWT-basierte Authentication mit Login-Endpoint (POST /auth/login),
Refresh-Token-Rotation und Rate-Limiting (max 5 Versuche/Minute)"

"Refactore diese Funktion: Extrahiere die Validierungslogik in eine eigene 
Funktion, verwende Early Returns statt verschachtelter if-Blöcke, und 
füge TypeScript-Typen hinzu"
```

## Wie vermeiden?

### ✅ Die 5 W-Fragen
- **Was** genau soll gebaut werden?
- **Wie** soll es technisch umgesetzt werden?
- **Welche** Constraints gelten?
- **Wohin** soll der Code?
- **Warum** diese Entscheidung?

### ✅ Beispiele geben
Ein Beispiel des gewünschten Outputs ist mehr wert als 100 Worte Beschreibung.

### ✅ Constraints explizit machen
Technologien, Patterns, Grenzen klar benennen.

## Schweregrad: 🟡 Mittel

Leicht zu beheben, aber überraschend weit verbreitet – besonders bei Einsteigern.
