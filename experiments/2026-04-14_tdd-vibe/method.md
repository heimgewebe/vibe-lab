---
title: "TDD-Vibe — Methode"
status: testing
canonicality: operative
---

# method.md — Experiment-Methode

## Hypothese

Test-First-Prompting (TDD-Vibe) — wobei das LLM zuerst eine vollständige Test-Suite generiert, die das gewünschte Verhalten beschreibt, und erst danach die Implementierung schreibt — produziert:

1. Mehr vollständige Fehlerbehandlung (Edge Cases werden im Test-Schritt explizit)
2. Weniger manuelle Nacharbeit nach der Generierung
3. Höheres Vertrauen in die Korrektheit des Ergebnisses

...als der übliche Implementation-First-Ansatz (Code zuerst, Tests danach oder gar nicht).

## Motivation

In `raw-vibes/prompt-fragmente.md` existiert der Impuls:
> "Write the tests for this component first. We will implement the component in the next step."

Dieser Ansatz wurde bisher nie formal evaluiert. Er schließt konzeptuell an Spec-First an (2026-04-08), nutzt aber **ausführbare Tests** statt formaler Specs als Anker — mit dem Unterschied, dass Fehlschläge maschinell nachweisbar werden, nicht nur subjektiv einschätzbar.

## Methode

### Vorgehen

1. **Setup:** Frisches TypeScript/Node.js-Projekt (identisch für beide Gruppen)
2. **Kontrollgruppe (Implementation-First):**
   - Aufgabe direkt mit Beschreibung an das Modell übergeben
   - Implementierung generieren
   - Optional: Tests danach schreiben
3. **Treatmentgruppe (TDD-Vibe):**
   - Aufgabe übergeben mit expliziter Anweisung: *"Generiere zuerst nur Tests. Kein Implementierungscode."*
   - Tests reviewen und validieren
   - Zweiter Prompt: *"Implementiere nun den Code so, dass alle Tests bestehen."*
4. **Beobachtung:** Ergebnisse anhand der definierten Metriken vergleichen
5. **Dokumentation:** Beobachtungen kontinuierlich in evidence.jsonl festhalten

### Benchmark

Challenge: **REST-API CRUD v1** (`benchmarks/challenges/rest-api-v1.md`)  
Ermöglicht direkten Vergleich mit den Spec-First-Ergebnissen aus 2026-04-08.

### Metriken

**Wirksamkeit (Effektivität):**
- Vollständigkeit der Fehlercodes (alle 7 geforderten HTTP-Status vorhanden?)
- Edge-Case-Abdeckung: Wie viele der Tests testen Fehlerpfade (4xx/5xx), nicht nur Happy Path?
- Validierungsabdeckung: Input-Validierung korrekt und vollständig?
- Test-Pass-Rate direkt nach Generierung (ohne manuellen Fix)

**Reibung (Aufwand):**
- Anzahl Prompts bis zum lauffähigen Ergebnis
- Manuelle Nacharbeit in Zeilen (Implementierungscode + Tests)
- Zeit bis zur ersten grünen Test-Suite

**Flow (subjektive Qualität):**
- Vertrauen in die Korrektheit (1–5 Skala)
- Gefühl der Kontrolle über die Implementierung (1–5 Skala)

### Erfolgskriterien

**Hypothese bestätigt**, wenn TDD-Vibe in mindestens 2 von 3 Metriken besser abschneidet:
- Mehr Fehlercodes vollständig implementiert
- Weniger manuelle Nacharbeit (Zeilen)
- Höhere Test-Pass-Rate direkt nach Generierung

**Hypothese widerlegt**, wenn kein messbarer Unterschied oder Implementation-First besser abschneidet.

## Variablen

| Variable             | Kontrollgruppe              | Treatmentgruppe (TDD-Vibe)            |
| -------------------- | --------------------------- | ------------------------------------- |
| Prompt-Strategie     | Direkte Beschreibung → Code | Test-Generierung → Implementierung    |
| Aufgabe              | REST-API CRUD v1            | REST-API CRUD v1 (identisch)          |
| Modell               | Claude claude-sonnet-4-6         | Claude claude-sonnet-4-6                   |
| Umgebung             | Node.js / Express.js        | Node.js / Express.js (identisch)      |
| Formales Artefakt    | Keines                      | Test-Suite als ausführbare Spec       |

## Abgrenzung zu Spec-First

| Aspekt             | Spec-First (2026-04-08)              | TDD-Vibe (dieses Experiment)          |
| ------------------ | ------------------------------------ | ------------------------------------- |
| Vorangestelltes Artefakt | OpenAPI-Spec (Beschreibungsform)  | Jest-Tests (ausführbare Form)         |
| Verifikation       | Manuell (spec review)               | Automatisch (npm test)                |
| Fehlschlag-Signal  | Subjektiv einschätzbar              | Maschinell nachweisbar                |
| Kombination möglich? | —                                   | Ja: Spec-First → TDD-Vibe als Combo  |

## Risiken und Einschränkungen

- Kleine Stichprobe (1 Benchmark-Task) begrenzt statistische Aussagekraft
- Ein einziger Experimentator — subjektive Bewertung der Metriken
- Test-Qualität im Test-First-Schritt selbst nicht formal validiert
- Modell-spezifische Ergebnisse: Claude claude-sonnet-4-6 könnte sich anders verhalten als GPT-4o
