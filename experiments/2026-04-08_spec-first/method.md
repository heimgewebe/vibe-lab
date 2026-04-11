---
title: "Spec-First Vibe-Coding — Methode"
status: adopted
canonicality: operative
---

# method.md — Experiment-Methode

## Hypothese

Ein vorangestellter Spezifikationsschritt (Spec-First) verbessert Konsistenz und Vollständigkeit von LLM-generiertem API-Code messbar gegenüber direktem "Generate from description".

## Methode

### Vorgehen

1. **Setup:** Frisches TypeScript/Express-Projekt erstellen (identisch für beide Gruppen)
2. **Kontrollgruppe (Direct):** 3 API-Tasks direkt mit einer natürlichsprachlichen Beschreibung an Copilot übergeben
3. **Treatmentgruppe (Spec-First):** Dieselben 3 Tasks, aber mit vorgelagertem Spec-Schritt (OpenAPI-Spec generieren → reviewen → dann implementieren)
4. **Beobachtung:** Ergebnisse vergleichen anhand der definierten Metriken
5. **Dokumentation:** Beobachtungen in evidence.jsonl festhalten

### Tasks
1. User CRUD API (Create, Read, Update, Delete)
2. Authentication Endpoint (Login, Token-Refresh)
3. Pagination + Filtering für List-Endpoints

### Metriken

- **Wirksamkeit (Effektivität):**
  - Vollständigkeit der Fehlercodes (alle relevanten HTTP-Status vorhanden?)
  - Validierungsabdeckung (Input-Validierung vorhanden?)
  - Konsistenz der Response-Strukturen
- **Reibung (Aufwand):**
  - Anzahl Prompts bis zum fertigen Ergebnis
  - Manuelle Nacharbeit (Zeilen geändert nach Generierung)
- **Flow (subjektive Qualität):**
  - Lesbarkeit des generierten Codes (1-5 Skala)
  - Vertrauen in die Korrektheit (1-5 Skala)

### Erfolgskriterien

- Hypothese bestätigt, wenn Spec-First in mindestens 2 von 3 Tasks bessere Werte in Vollständigkeit UND weniger Nacharbeit zeigt.
- Hypothese widerlegt, wenn kein messbarer Unterschied oder Direct besser abschneidet.

## Variablen

| Variable            | Beschreibung                  | Kontrolle          | Treatment             |
| ------------------- | ----------------------------- | ------------------ | --------------------- |
| Prompt-Strategie    | Wie der Task übergeben wird   | Direkte Beschreibung | Spec-First (2 Schritte) |
| Task-Komplexität    | Schwierigkeit der Aufgabe     | Identisch          | Identisch             |
| Modell              | Verwendetes LLM               | GPT-4o             | GPT-4o                |
| Umgebung            | IDE + Setup                   | VS Code + Copilot  | VS Code + Copilot     |

## Risiken und Einschränkungen

- Kleine Stichprobe (3 Tasks) begrenzt statistische Aussagekraft
- Ein einzelner Experimentator — subjektive Bewertung
- Nur ein Modell getestet; Ergebnisse möglicherweise modellspezifisch
