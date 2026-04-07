---
name: "Full-Auto Generation"
category: style
maturity: experimental
tools: [cursor, claude-code, aider, devin]
synergies: [spec-first-vibe, context-stuffing, multi-file-generation]
anti-synergies: [pair-programming-mit-ki]
complexity: high
speed_boost: "10x"
quality_impact: "-"
tags: [automation, autonomous, agent, full-stack]
last_tested: 2026-04-01
---

# 🤖 Full-Auto Generation

## Beschreibung

Full-Auto Generation überlässt der KI die **komplette Code-Generierung** – vom Projektsetup über die Implementierung bis hin zu Tests und Dokumentation. Der Mensch gibt nur das Ziel vor und reviewt das Endergebnis.

## Wie es funktioniert

1. **Ziel definieren**: Ausführliche Beschreibung des gewünschten Endprodukts
2. **Kontext bereitstellen**: Bestehender Code, Tech-Stack, Qualitätsanforderungen
3. **Generieren lassen**: Die KI erstellt alle Dateien
4. **Review**: Gesamtergebnis prüfen und ggf. nachbessern

## Beispiel

```
"Erstelle eine vollständige REST-API für ein Bookstore-Management:
- Node.js + Express + TypeScript
- PostgreSQL mit Prisma ORM
- CRUD für Books, Authors, Categories
- JWT Authentication
- Input Validation mit Zod
- Unit und Integration Tests mit Vitest
- Docker Compose Setup
- API Documentation mit Swagger
- Ordnerstruktur: feature-basiert
Erstelle ALLE Dateien, die für ein lauffähiges Projekt nötig sind."
```

## Wann einsetzen?

- ✅ Greenfield-Projekte mit klarem Scope
- ✅ Standardisierte Anwendungen (CRUD-APIs, Dashboards)
- ✅ Prototypen und MVPs
- ✅ Boilerplate-Heavy-Projekte
- ❌ Bestehende komplexe Codebases
- ❌ Hochspezialisierte Domänen
- ❌ Wenn Verständnis des Codes wichtig ist

## Stärken

- **Maximale Geschwindigkeit** – ganze Projekte in Minuten
- **Konsistente Struktur** – KI hält sich an ein einheitliches Pattern
- **Vollständig** – nichts wird vergessen (Tests, Types, Config)
- **Inspirierend** – man sieht schnell das große Bild

## Schwächen

- **Black Box** – man versteht den generierten Code nicht vollständig
- **Fehleranfällig bei Komplexität** – bei vielen Anforderungen steigt die Fehlerquote
- **Schwer zu debuggen** – wenn etwas nicht funktioniert, wo anfangen?
- **Vendor Lock-in-Gefahr** – generierter Code folgt KI-Patterns, nicht Team-Patterns

## Bewertung

| Dimension | Score | Kommentar |
|-----------|:-----:|-----------|
| ⏱️ Geschwindigkeit | 5/5 | Unschlagbar für initiale Generierung |
| 🎯 Treffsicherheit | 2/5 | Oft 80% richtig, 20% manuell |
| 🏗️ Codequalität | 3/5 | Strukturell ok, aber Details oft mangelhaft |
| 🔄 Iterationsfähigkeit | 2/5 | Schwer punktuell zu ändern |
| 🧠 Kognitive Last | 2/5 | Review-Last ist hoch |
| 📐 Skalierbarkeit | 3/5 | Gut für Greenfield, schlecht für Brownfield |
| 🎨 Kreativität | 3/5 | Standardlösungen, gelegentlich kreativ |

## Verwandte Einträge

- **Synergie**: [Spec-First Vibe](spec-first-vibe.md)
- **Gegensatz**: [Pair-Programming mit KI](pair-programming-mit-ki.md)
- **Tool**: [Cursor Composer](../technologies/cursor.md)
