---
title: "Incremental vs. Single-Shot: Debuggability — Methode"
status: designed
canonicality: operative
---

# method.md — Experiment-Methode

## Hypothese

Bei Task 2 (CSV CLI) und dem bekannten doppelten `i++`-Bug im CLI-Argument-Parser erlaubt der
modulare Incremental-Artefaktzustand eine frühere Lokalisierung (`first_failing_input_index`)
oder schnellere Behebung (`time_to_fix`) als der monolithische Single-Shot-Artefaktzustand —
gemessen an tatsächlicher Ausführung mit 5 definierten Inputs.

**Bewusstes Scope-Limit:** Diese Hypothese urteilt nicht über Incremental Refinement als
allgemeine Strategie. Sie ist eng gebunden an: diesen Task, diesen Bugtyp, diese zwei
Artefaktzustände. Verallgemeinerungen erfordern weitere Experimente.

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

**Phase 3 — Bug-Behebung (Fix-Iteration, Dual-Modus)**

12. Für jede Variante werden **zwei Fix-Modi** durchgeführt — in dieser Reihenfolge:

    **Modus A — Unguided Fix** (kein Pfadhinweis):
    - Single-Shot: Prompt „Behebe den Bug, der Input 3 und 4 fehlschlagen lässt."
    - Incremental: identischer Prompt ohne Nennung von `cli.ts`
    - `time_to_fix_unguided`: Anzahl Prompts bis korrektes Output auf allen 5 Inputs

    **Modus B — Guided Fix** (Lokalisierung vorgegeben):
    - Single-Shot: Prompt „Der Bug liegt im Argument-Parser in `index.ts`. Behebe ihn."
    - Incremental: Prompt „Der Bug liegt in `cli.ts`. Behebe ihn."
    - `time_to_fix_guided`: Anzahl Prompts bis korrektes Output auf allen 5 Inputs

    Begründung: Guided vs. unguided trennt *Strukturvorteil* (Incremental-Module sind isolierbar)
    von *Strategie-Effekt* (Incremental macht Bugs inhärent sichtbarer). Nur unguided misst
    echten Suchaufwand; guided misst Fix-Einfachheit nach Lokalisierung.

13. `patch_size` für beide Modi messen: Zeilen geändert im Fix-Diff (git diff --stat)

**Phase 4 — Vergleich und Dokumentation**

15. Alle Metriken in evidence.jsonl eintragen
16. decision.yml und result.md befüllen

### Metriken

**Primärmetriken (neu, hartmessbar):**

| Metrik | Definition | Einheit | Hinweis |
| ------ | ---------- | ------- | ------- |
| `first_failing_input_index` | Index des ersten Inputs (1–5) mit falschem Output | Ganzzahl (1–5) | Früher Name `time_to_first_bug_detection` war irreführend: kein echtes Discovery-Szenario, da Bug und Trigger-Inputs bekannt sind. Diese Metrik misst Position in der Test-Sequenz, nicht Entdeckungszeit. |
| `time_to_fix_unguided` | Prompts vom Bug-Fund bis korrektes Output auf allen 5 Inputs — ohne Pfadhinweis | Ganzzahl | Misst echten Suchaufwand (Lokalisierung + Fix) |
| `time_to_fix_guided` | Prompts vom Bug-Fund bis korrektes Output — mit Pfadhinweis auf Datei | Ganzzahl | Misst Fix-Aufwand nach bekannter Lokalisierung (Strukturvorteil isoliert) |
| `hidden_bugs_count` | Anzahl Bugs, die nur durch Ausführung (nicht Kompilierung) gefunden wurden | Ganzzahl | |
| `patch_size` | Zeilen geändert im Fix-Diff (git diff --stat) | Zeilen | Pro Fix-Modus getrennt erfassen |

**Sekundärmetriken (aus Vorgänger, zur Kontextualisierung):**

| Metrik | Definition |
| ------ | ---------- |
| `compilation_errors` | 0 oder >0 — erwartbar 0 für beide |
| `correct_outputs` | Anzahl korrekte Outputs auf 5 Inputs (vor Fix) |
| `fix_scope` | Muss nur ein Modul / eine Datei geändert werden? |

**Ausdrücklich NICHT als Qualitätsbeweis gewertet:**
- Anzahl Dateien, Typen, Fehlerklassen, Exports (Proxy-Metriken aus Vorgänger)

### Erfolgskriterien

- **Hypothese bestätigt (Lokalisierungsvorteil):** Incremental hat `first_failing_input_index` ≤
  Single-Shot UND `time_to_fix_unguided` ≤ Single-Shot
- **Hypothese bestätigt (Strukturvorteil isoliert):** `time_to_fix_guided` Incremental < Single-Shot,
  aber `time_to_fix_unguided` nicht besser → Vorteil liegt in Modul-Isolation, nicht in Strategie
- **Hypothese widerlegt:** Single-Shot hat gleiche oder bessere Werte auf beiden unguided-Metriken
- **Inconclusive:** Gemischte Ergebnisse über Fix-Modi hinweg, oder beide Arme bug-frei

### Tasks

Einziger Task: **Task 2 — CSV CLI-Tool** aus dem Vorgängerexperiment.
Fokus-Begründung: Enthielt bekannten Laufzeitbug trotz korrekter Kompilierung; CLI-Tool
ist eindeutig testbar durch Input-Output-Vergleich.

## Variablen

| Variable | Beschreibung | Kontrolle (Single-Shot) | Treatment (Incremental) |
| -------- | ------------ | ----------------------- | ----------------------- |
| Prompt-Strategie | Generierungsstrategie | 1 umfassender Prompt | 6 gezielte Teilprompts |
| Ausgangszustand | Welche Artefaktversion | Originales Single-Shot (bug-frei) | Incremental mit revertiertem Bug (dokumentiert in INITIAL.md) |
| Ausführungsumgebung | Runtime | Identisch (ts-node) | Identisch (ts-node) |
| Test-Inputs | CSV-Szenarien | 5 definierte Inputs (identisch) | 5 definierte Inputs (identisch) |
| Fix-Methode A (unguided) | Prompt ohne Datei-/Modulhinweis | Identischer Prompt | Identischer Prompt |
| Fix-Methode B (guided) | Prompt mit explizitem Dateinamen | Hinweis auf `index.ts` | Hinweis auf `cli.ts` |

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
