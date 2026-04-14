---
title: "Incremental Refinement vs. Single-Shot — Methode"
status: designed
canonicality: operative
---

# method.md — Experiment-Methode

## Hypothese

Inkrementelle Code-Generierung durch viele kleine, gezielte Prompts führt zu besserer Codequalität (weniger Bugs, bessere Struktur) und weniger manueller Nacharbeit als Single-Shot-Generierung — auf Kosten einer höheren Gesamtzahl an Prompts.

## Methode

### Vorgehen

1. **Setup:** Frisches TypeScript/Node.js-Projekt erstellen (identisch für beide Gruppen)
2. **Kontrollgruppe (Single-Shot):** 3 Feature-Tasks jeweils in einem einzelnen, umfassenden Prompt an das LLM übergeben. Das Ergebnis wird ohne weitere Prompt-Interaktion übernommen.
3. **Treatmentgruppe (Incremental):** Dieselben 3 Tasks, aber in kleine Teilschritte zerlegt:
   - Schritt 1: Datenmodell / Typen generieren
   - Schritt 2: Grundstruktur / Routing generieren
   - Schritt 3: Kernlogik generieren
   - Schritt 4: Fehlerbehandlung ergänzen
   - Schritt 5: Validierung hinzufügen
   - Schritt 6: Tests generieren
4. **Beobachtung:** Ergebnisse anhand der definierten Metriken vergleichen
5. **Dokumentation:** Beobachtungen in evidence.jsonl festhalten

### Tasks

1. REST-API für ein Bookmark-System (CRUD + Tags + Suche)
2. CLI-Tool zum Parsen und Transformieren von CSV-Daten
3. Middleware-Stack mit Rate-Limiting, Auth-Check und Request-Logging

### Metriken

- **Wirksamkeit (Effektivität):**
  - Fehleranzahl im generierten Code (TypeScript-Kompilierungsfehler, Laufzeitfehler)
  - Vollständigkeit der Anforderungen (alle geforderten Features vorhanden?)
  - Testbarkeit (lässt sich der Code ohne Umstrukturierung testen?)
- **Reibung (Aufwand):**
  - Anzahl Prompts bis zum fertigen Ergebnis
  - Manuelle Nacharbeit (Zeilen geändert nach Generierung)
  - Gesamtzeit pro Task
- **Flow (subjektive Qualität):**
  - Code-Lesbarkeit (1–5 Skala)
  - Architektonische Kohärenz (1–5 Skala: Sind Schichten, Verantwortlichkeiten und Abstraktionen konsistent?)
  - Vertrauen in die Korrektheit (1–5 Skala)

### Erfolgskriterien

- Hypothese bestätigt, wenn Incremental in mindestens 2 von 3 Tasks weniger Fehler UND weniger Nacharbeit produziert als Single-Shot.
- Hypothese widerlegt, wenn Single-Shot gleichwertige oder bessere Ergebnisse liefert.
- Inconclusive, wenn die Ergebnisse gemischt sind oder die Varianz zu groß ist.

## Variablen

| Variable              | Beschreibung                           | Kontrolle (Single-Shot) | Treatment (Incremental)       |
| --------------------- | -------------------------------------- | ----------------------- | ----------------------------- |
| Prompt-Strategie      | Wie der Task ans LLM übergeben wird   | 1 umfassender Prompt    | 5–6 gezielte Teilprompts      |
| Task-Komplexität      | Schwierigkeit der Aufgabe              | Identisch               | Identisch                     |
| Modell                | Verwendetes LLM                        | Identisch               | Identisch                     |
| Umgebung              | IDE + Setup                            | Identisch               | Identisch                     |
| Menschlicher Eingriff | Review/Edit zwischen Schritten         | Keine Zwischenschritte  | Review nach jedem Teilschritt |

## Risiken und Einschränkungen

- Kleine Stichprobe (3 Tasks) begrenzt statistische Aussagekraft
- Das Zerlegen in Teilschritte ist selbst eine kreative Leistung — verschiedene Zerlegungen können zu unterschiedlichen Ergebnissen führen
- Der Review nach jedem Teilschritt in der Incremental-Gruppe bringt zusätzlichen menschlichen Input ein, der den Vergleich verzerren kann
- Nur ein Modell getestet; Ergebnisse möglicherweise modellspezifisch
- Die Zeitmessung erfasst nicht den kognitiven Aufwand der Prompt-Planung
