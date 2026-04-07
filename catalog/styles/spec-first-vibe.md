---
name: "Spec-First Vibe"
category: style
maturity: proven
tools: [cursor, claude-code, aider, copilot]
synergies: [chain-of-thought, context-stuffing, tdd-vibe]
anti-synergies: [yolo-prompting]
complexity: medium
speed_boost: "2x"
quality_impact: "++"
tags: [architecture, planning, specification, production]
last_tested: 2026-04-01
---

# 📋 Spec-First Vibe

## Beschreibung

Beim Spec-First Vibe wird **zuerst eine Spezifikation** erstellt – durch den Menschen, die KI, oder beide zusammen – bevor auch nur eine Zeile Code geschrieben wird. Die Spezifikation dient als Vertrag zwischen Mensch und KI.

## Wie es funktioniert

1. **Spezifikation erstellen**: Beschreibe die Anforderungen in strukturierter Form
2. **Review**: Lass die KI die Spec reviewen und ergänzen
3. **Implementation**: Lass die KI auf Basis der Spec implementieren
4. **Validation**: Prüfe den Output gegen die Spec

## Beispiel

```markdown
## Spezifikation: User Authentication Service

### Anforderungen
- JWT-basierte Authentication
- Refresh-Token-Rotation
- Rate-Limiting (max 5 Login-Versuche pro Minute)

### API Endpoints
- POST /auth/login → { accessToken, refreshToken }
- POST /auth/refresh → { accessToken, refreshToken }
- POST /auth/logout → 204

### Technologie
- Node.js + Express
- PostgreSQL für User-Daten
- Redis für Token-Blacklist

### Qualitätsanforderungen
- 100% Testabdeckung der Auth-Logik
- Input-Validierung mit Zod
- Structured Logging
```

## Wann einsetzen?

- ✅ Produktionscode mit klaren Anforderungen
- ✅ Sicherheitskritische Komponenten
- ✅ Team-Projekte, wo Konsistenz wichtig ist
- ✅ Komplexe Features mit vielen Randfällen
- ❌ Schnelle Prototypen
- ❌ Explorative Aufgaben ("Mal schauen was geht")
- ❌ Wenn die Anforderungen noch unklar sind

## Stärken

- **Hohe Codequalität** – die Spec lenkt die KI zu besseren Lösungen
- **Reproduzierbar** – gleiche Spec → ähnliches Ergebnis
- **Gut iterierbar** – Änderungen an der Spec = Änderungen am Code
- **Dokumentation inklusive** – die Spec IST die Dokumentation
- **Skaliert gut** – auch für größere Projekte geeignet

## Schwächen

- **Langsamer Start** – Spec schreiben braucht Zeit
- **Overhead bei kleinen Aufgaben** – manchmal ist die Spec länger als der Code
- **Erfordert Erfahrung** – gute Specs schreiben ist eine eigene Fähigkeit
- **Rigide** – spontane Änderungen erfordern Spec-Updates

## Bewertung

| Dimension | Score | Kommentar |
|-----------|:-----:|-----------|
| ⏱️ Geschwindigkeit | 3/5 | Langsamer Start, aber weniger Iterationen |
| 🎯 Treffsicherheit | 4/5 | Klare Vorgaben = klare Ergebnisse |
| 🏗️ Codequalität | 4/5 | Spec erzwingt Struktur |
| 🔄 Iterationsfähigkeit | 4/5 | Spec-Änderungen → Code-Änderungen |
| 🧠 Kognitive Last | 3/5 | Spec-Erstellung erfordert Nachdenken |
| 📐 Skalierbarkeit | 4/5 | Gut für große Projekte |
| 🎨 Kreativität | 2/5 | Spec schränkt Kreativität ein |

## Verwandte Einträge

- **Synergie**: [Chain-of-Thought Driven Development](../techniques/chain-of-thought.md)
- **Synergie**: [TDD-Vibe](tdd-vibe.md)
- **Gegensatz**: [YOLO-Prompting](yolo-prompting.md)
