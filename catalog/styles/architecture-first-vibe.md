---
name: "Architecture-First Vibe"
category: style
maturity: experimental
tools: [cursor, claude-code, chatgpt]
synergies: [spec-first-vibe, chain-of-thought, context-stuffing]
anti-synergies: [yolo-prompting]
complexity: high
speed_boost: "2x"
quality_impact: "+++"
tags: [architecture, design, planning, enterprise, scalability]
last_tested: 2026-04-01
---

# 🏛️ Architecture-First Vibe

## Beschreibung

Beim Architecture-First Vibe wird **zuerst die gesamte Architektur** mit der KI entworfen – Systemdiagramme, Komponentenstruktur, Datenflüsse, API-Contracts – bevor eine einzige Zeile Implementierungscode geschrieben wird.

## Wie es funktioniert

1. **Vision beschreiben**: Was soll das System leisten?
2. **Architektur designen**: KI erstellt Komponentendiagramm, Datenmodell, API-Design
3. **Review & Iteration**: Architektur gemeinsam verfeinern
4. **Implementierungsplan**: Reihenfolge der Komponenten festlegen
5. **Komponentenweise implementieren**: Jede Komponente einzeln generieren

## Beispiel

```
"Entwirf die Architektur für einen E-Commerce-Marketplace:
- Microservices-Architektur
- Event-Driven Communication
- Zeige mir: Komponentendiagramm, Datenmodell, API-Contracts
- Technologievorschläge für jede Komponente
Noch KEINEN Code – nur Architektur und Design."
```

## Wann einsetzen?

- ✅ Große, komplexe Projekte
- ✅ Systeme mit vielen Komponenten
- ✅ Enterprise-Anwendungen
- ✅ Wenn langfristige Wartbarkeit wichtig ist
- ❌ Kleine Features und Skripte
- ❌ Prototypen und MVPs
- ❌ Wenn die Domäne noch nicht verstanden ist

## Stärken

- **Beste Skalierbarkeit** – Architektur trägt das Projekt langfristig
- **Konsistenz** – alle Komponenten folgen dem gleichen Design
- **Dokumentation** – Architektur-Dokumente als Nebenprodukt
- **KI als Architekt** – bringt Patterns und Best Practices ein

## Schwächen

- **Langsam** – viel Vorabplanung
- **Overengineering-Gefahr** – für kleine Projekte überdimensioniert
- **KI-Architektur-Grenzen** – KI tendiert zu bekannten Patterns
- **Erfordert Architektur-Wissen** – man muss die Vorschläge bewerten können

## Bewertung

| Dimension | Score | Kommentar |
|-----------|:-----:|-----------|
| ⏱️ Geschwindigkeit | 2/5 | Langsamer Start, zahlt sich langfristig aus |
| 🎯 Treffsicherheit | 4/5 | Klare Architektur = klare Implementierung |
| 🏗️ Codequalität | 5/5 | Architektur erzwingt Qualität |
| 🔄 Iterationsfähigkeit | 3/5 | Architektur-Änderungen sind aufwändig |
| 🧠 Kognitive Last | 2/5 | Hohe Denkarbeit in der Designphase |
| 📐 Skalierbarkeit | 5/5 | Genau dafür gemacht |
| 🎨 Kreativität | 3/5 | KI kann kreative Architekturen vorschlagen |

## Verwandte Einträge

- **Synergie**: [Spec-First Vibe](spec-first-vibe.md)
- **Synergie**: [Context Stuffing](../techniques/context-stuffing.md)
- **Gegensatz**: [YOLO-Prompting](yolo-prompting.md)
