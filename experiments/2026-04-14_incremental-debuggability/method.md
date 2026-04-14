---
title: "Incremental vs. Single-Shot: Debuggability — Methode"
status: designed
canonicality: operative
---

# method.md — Experiment-Methode

## Hypothese

Incremental Refinement ermöglicht frühere Bug-Erkennung und schnellere Bug-Behebung als
Single-Shot — gemessen an `time_to_first_bug_detection`, `time_to_fix` und `hidden_bugs_count`
nach tatsächlicher Ausführung des generierten Codes.

## Methode

### Vorgehen

**Phase 0 — Setup**

1. Beide Varianten aus `2026-04-14_incremental-refinement` als neue Kopie anlegen:
   - `artifacts/task2-single-shot/` (Single-Shot CSV CLI)
   - `artifacts/task2-incremental/` (Incremental CSV CLI — mit dem ursprünglichen Bug revertiert)
2. `npm init` + `tsc --init` für beide Varianten identisch konfigurieren
3. Die 5 Testdaten-CSVs aus INITIAL.md anlegen

**Phase 1 — Ausführung und Bug-Erhebung (Kontrolle: Single-Shot)**

4. Jeden der 5 Inputs ausführen: `ts-node index.ts <args>`
5. Tatsächliche vs. erwartete Ausgabe dokumentieren
6. Für jede Abweichung: als `hidden_bug` in evidence.jsonl festhalten
7. `time_to_first_bug_detection`: Anzahl Ausführungsversuche, bis erste Abweichung sichtbar

**Phase 2 — Ausführung und Bug-Erhebung (Treatment: Incremental)**

8. Gleiche 5 Inputs mit Incremental-Variante ausführen (mit revertiertem Bug)
9. Tatsächliche vs. erwartete Ausgabe dokumentieren
10. Bug-Erkennung: bei welchem Input / welcher Iteration fällt der Bug auf?
11. `time_to_first_bug_detection` für Incremental festhalten

**Phase 3 — Bug-Behebung (Fix-Iteration)**

12. Für jede Variante: einen einfachen Fix-Prompt formulieren und anwenden
    - Single-Shot: Ein Prompt zum Beheben des identifizierten Fehlers
    - Incremental: Bug im spezifischen Modul (`cli.ts`) beheben, dann System re-testen
13. `time_to_fix` messen: Anzahl Prompts bis zum korrekten Output auf allen 5 Inputs
14. `patch_size` messen: Zeilen geändert im Fix-Diff (git diff --stat)

**Phase 4 — Vergleich und Dokumentation**

15. Alle Metriken in evidence.jsonl eintragen
16. decision.yml und result.md befüllen

### Metriken

**Primärmetriken (neu, hartmessbar):**

| Metrik | Definition | Einheit |
| ------ | ---------- | ------- |
| `time_to_first_bug_detection` | Anzahl Test-Inputs bis erstes falsches Ergebnis sichtbar | Ganzzahl (1–5) |
| `time_to_fix` | Anzahl Prompts vom Bug-Fund bis korrektes Output auf allen 5 Inputs | Ganzzahl |
| `hidden_bugs_count` | Anzahl Bugs, die nur durch Ausführung (nicht Kompilierung) gefunden wurden | Ganzzahl |
| `patch_size` | Zeilen geändert im Bug-Fix (git diff --stat) | Zeilen |

**Sekundärmetriken (aus Vorgänger, zur Kontextualisierung):**

| Metrik | Definition |
| ------ | ---------- |
| `compilation_errors` | 0 oder >0 — erwartbar 0 für beide |
| `correct_outputs` | Anzahl korrekte Outputs auf 5 Inputs (vor Fix) |
| `fix_scope` | Muss nur ein Modul / eine Datei geändert werden? |

**Ausdrücklich NICHT als Qualitätsbeweis gewertet:**
- Anzahl Dateien, Typen, Fehlerklassen, Exports (Proxy-Metriken aus Vorgänger)

### Erfolgskriterien

- **Hypothese bestätigt:** Incremental hat `time_to_first_bug_detection` ≤ Single-Shot
  UND `time_to_fix` ≤ Single-Shot (d.h. Bugs werden schneller gefunden und behoben)
- **Hypothese widerlegt:** Single-Shot hat gleiche oder bessere Werte bei beiden Primärmetriken
- **Inconclusive:** Gemischte Ergebnisse (z.B. Incremental findet Bug früher, braucht aber
  mehr Aufwand zum Fixen) oder beide Arme haben keine verborgenen Bugs

### Tasks

Einziger Task: **Task 2 — CSV CLI-Tool** aus dem Vorgängerexperiment.
Fokus-Begründung: Enthielt bekannten Laufzeitbug trotz korrekter Kompilierung; CLI-Tool
ist eindeutig testbar durch Input-Output-Vergleich.

## Variablen

| Variable | Beschreibung | Kontrolle (Single-Shot) | Treatment (Incremental) |
| -------- | ------------ | ----------------------- | ----------------------- |
| Prompt-Strategie | Generierungsstrategie | 1 umfassender Prompt | 6 gezielte Teilprompts |
| Ausgangszustand | Welche Artefaktversion | Originales Single-Shot | Incremental mit revertiertem Bug |
| Ausführungsumgebung | Runtime | Identisch (ts-node) | Identisch (ts-node) |
| Test-Inputs | CSV-Szenarien | 5 definierte Inputs | 5 definierte Inputs (identisch) |
| Fix-Methode | Wie wird der Bug behoben | Ein Fix-Prompt (ganzes File) | Ein Fix-Prompt (nur betroffenes Modul) |

## Risiken und Einschränkungen

- **Experimentator-Bias bleibt:** Gleicher Agent für beide Arme; Incremental-Arm profitiert
  von isolierbaren Modulen beim Fixen (struktureller Vorteil, nicht nur Strategie-Effekt)
- **Einzelner Task:** Task 2 kann repräsentativ sein, muss es aber nicht; Generalisierung
  erfordert weitere Tasks und Sprachen
- **Bug ist bekannt:** Der Experimentator kennt den Incremental-Bug bereits; das kann die
  Suchreihenfolge beeinflussen → bewusstes Gegensteuern nötig (systematische Input-Reihenfolge)
- **„Fix-Aufwand" ist kontextabhängig:** Incremental erlaubt Modul-gezieltes Fixen — das ist
  ein systemischer Vorteil, der separat dokumentiert werden muss, nicht als reiner Strategie-Effekt
- **Rückwärtskompatibilität:** Der revertierte Bug ist dokumentiert; Vergleich ist nur
  valide, wenn Revert sauber durchgeführt und dokumentiert wird
