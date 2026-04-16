---
title: "Incremental Refinement vs. Single-Shot — Ergebnis"
status: inconclusive
canonicality: operative
---

# result.md — Experiment-Ergebnis

## Zusammenfassung

**Incremental Refinement erzeugt sichtbar modulareren Code als Single-Shot** — in allen drei Tasks. Die Verbesserungen zeigen sich in Architektur (Dateitrennung, Separation of Concerns), expliziter Typisierung (mehr Interfaces) und strukturierter Fehlerbehandlung (dedizierte Fehlerklassen).

Allerdings reicht die vorliegende Evidenz nicht für ein belastbares Verdict. Die verwendeten Metriken sind überwiegend Proxy-Metriken (Dateien, Typen, Error-Handling-Konstrukte), die Modularität belegen, aber nicht automatisch Korrektheit oder Wartbarkeit. Es fehlen Laufzeittests, tatsächliche Testdateien und gemessene Nacharbeits-Diffs. Zudem enthielt der Incremental-Arm einen substantiellen Laufzeitbug (Task 2 CLI-Parser), der trotz fehlerfreier Kompilierung unentdeckt blieb.

**Verdict: inconclusive** — starker Designhinweis, aber noch kein robuster Wirknachweis.

## Beobachtungen

### Wirksamkeit (Effektivität)

| Metrik                     | Single-Shot   | Incremental   | Differenz |
| -------------------------- | ------------- | ------------- | --------- |
| Kompilierungsfehler        | 0/3           | 0/3           | Kein Unterschied |
| Laufzeitbugs (gefunden)    | 0             | 1 (Task 2)    | Incremental schlechter |
| Types/Interfaces (Ø)       | 3.3           | 6.7           | +103% (Proxy-Metrik) |
| Error-Handling-Konstrukte (Ø) | 1.0        | 8.7           | +770% (Proxy-Metrik) |
| Architektur                | Monolithisch  | Modular       | Qualitativ besser |
| Testdateien erzeugt        | 0/3           | 0/3           | Kein Unterschied |

**Wichtig:** Mehr Types und Error-Handling-Konstrukte belegen Modularität, aber nicht automatisch bessere Software. Typkorrekt ist nicht gleich laufzeitkorrekt — der Task-2-Bug zeigt das exemplarisch.

**Vollständigkeit (plausibel, nicht verifiziert):** Incremental-Code scheint mehr Edge Cases abzudecken:
- Task 1: Leere Titel werden validiert, PaginatedResponse hat totalPages-Feld
- Task 2: Unbekannte CLI-Flags werden gemeldet, RegExp-Escape bei Replace — **aber** CLI-Parser hatte doppeltes `i++`-Bug, das Argumente überspringt
- Task 3: Memory-Leak-Schutz im Rate Limiter (Cleanup-Interval), Request-ID-Tracing

### Laufzeitbug: Task 2 Incremental CLI-Parser

In `artifacts/task2-incremental/cli.ts` enthielt der Argument-Parser ein systematisches Double-Increment-Pattern:

```typescript
case '--input':
case '-i':
  options.inputPath = requireNextArg(args, i++, 'input');  // i++ hier
  i++;                                                      // und nochmal hier
  break;
```

`requireNextArg(args, i++, 'input')` inkrementiert `i` (Post-Inkrement), danach folgt ein weiteres `i++`, plus das `i++` der for-Schleife. Resultat: nach jedem Flag mit Wert wird das nächste Argument übersprungen. Dieses Pattern trat in allen 7 switch-cases auf.

**Bedeutung:** Der Incremental-Arm produzierte trotz modularer Architektur und strukturierter Fehlerbehandlung einen substantiellen Laufzeitbug. Die Kompilierung (`tsc --noEmit --strict`) erkannte den Bug nicht. Das untergräbt den Claim "3/3 klare Siege" und illustriert: Separation of Concerns schützt nicht vor semantischen Fehlern.

Der Bug wurde im Rahmen der Review-Gegenprüfung gefixt.

### Reibung (Aufwand)

| Metrik               | Single-Shot | Incremental | Differenz |
| -------------------- | ----------- | ----------- | --------- |
| Prompts pro Task     | 1           | 6           | 6× mehr |
| Dateien pro Task     | 1           | 7           | 7× mehr |
| Ø Zeilen pro Task    | 188         | 402         | 2.1× mehr |
| Rework (geschätzt)   | 30–50%      | <10%        | Nur Schätzung, nicht gemessen |
| Ø Exports pro Task   | 1           | 16          | Mehr Kompositionsfähigkeit |

**Einschränkung Rework:** Die Werte sind Einschätzungen des Experimentators, keine gemessenen Patch-Diffs. Als Arbeitshypothese plausibel, als Evidenz-Pfeiler zu weich.

### Flow (subjektive Qualität)

| Metrik                     | Single-Shot | Incremental |
| -------------------------- | ----------- | ----------- |
| Code-Lesbarkeit            | 3/5         | 4/5         |
| Architektonische Kohärenz  | 2/5         | 5/5         |
| Vertrauen in Korrektheit   | 3/5         | 3/5 (nach Bugfund korrigiert) |

**Korrektur:** Das Vertrauen in die Korrektheit des Incremental-Arms wurde nach dem Bugfund von 4/5 auf 3/5 korrigiert.

### Fehlende Tests

Die Methode definiert Schritt 6 als "Tests generieren". In keiner der 6 Varianten wurden Testdateien erzeugt. Der Claim "bessere Testbarkeit" stützt sich daher auf architektonische Plausibilität (isolierte Exports), nicht auf tatsächlich existierende und laufende Tests.

## Deutung

### Was belegt ist

1. **Incremental erzeugt modulareren Code.** In 3/3 Tasks: getrennte Dateien für Typen, Kernlogik, Routing, Fehlerbehandlung, Validierung. Die These „Schrittzerlegung fördert Separation of Concerns" ist stark plausibel.
2. **Incremental erzeugt explizitere Typisierung.** Mehr Interfaces, mehr benannte Fehlerklassen, mehr Exports. Das ist real und messbar.
3. **Beide Strategien erzeugen typkorrekten Code.** 0 Kompilierungsfehler in allen 6 Varianten.

### Was nicht belegt ist

1. **Weniger Bugs.** Der Laufzeitbug in Task 2 widerspricht dem. Modularität ≠ Korrektheit.
2. **Bessere Testbarkeit.** Plausibel, aber nicht belegt — keine Tests vorhanden.
3. **Weniger Rework.** Geschätzt, nicht gemessen. Keine Patch-Diffs.
4. **„3/3 klare Siege."** Durch den Task-2-Bug epistemisch überzogen.

### Zwei plausible Lesarten

**Lesart A:** Incremental ist wirklich besser, weil die Schrittzerlegung Fokus und Struktur erzwingt.

**Lesart B:** Der Agent hatte bei Incremental 6 Anläufe statt 1 — das misst weniger „Strategieeffekt" als „mehr Bearbeitungszeit + Strukturzwang".

Beides ist hoch plausibel. Die Synthese: **Das Experiment zeigt einen starken Designhinweis, aber noch keinen robusten Wirknachweis.**

### Warum funktioniert es (plausibel)?

1. **Fokus-Effekt:** Jeder Teilprompt hat einen klar begrenzten Scope.
2. **Emergente Modularität:** Die Zerlegung in Schritte erzwingt Dateitrennung, die zu Separation of Concerns führt.
3. **Kumulativer Kontext:** Jeder Schritt baut auf dem vorherigen auf.

### Methodische Schwächen

1. **Experimentator-Bias:** Derselbe Agent erzeugte beide Arme mit derselben Meta-Intention.
2. **Proxy-Metriken als Qualitätsbeweis:** Mehr Dateien, Typen, Fehlerklassen sind nicht automatisch bessere Software.
3. **Fehlende Laufzeitvalidierung:** Kompilierung zeigt nur Syntax- und Typkorrektheit, nicht Semantik.
4. **Kein blinder Review:** Der Experimentator bewertete seinen eigenen Output.

## Verdict

**inconclusive** — Starker Designhinweis pro Incremental Refinement, aber die Evidenz reicht nicht für eine belastbare Adoption.

Die Kernthese (Schrittzerlegung fördert modulare Architektur) ist plausibel bis stark plausibel. Die weitergehenden Claims (weniger Bugs, bessere Testbarkeit, weniger Rework) sind nicht durch die vorliegende Evidenz gedeckt.

## Lessons Learned

1. **Modularität ist kein Zufall.** Incremental erzwingt Modularität durch die Zerlegung — das ist ein systemischer Effekt, kein Prompt-Trick.
2. **Proxy-Metriken sind keine Qualitätsbeweise.** Mehr Dateien, Typen und Fehlerklassen belegen Struktur, nicht Korrektheit. Architekturkosmetik kann Overhead sein.
3. **Typkorrekt ≠ laufzeitkorrekt.** Der Task-2-Bug zeigt: auch modularer, gut typisierter Code kann semantisch fehlerhaft sein. `tsc --noEmit --strict` prüft Syntax und Typen, nicht Verhalten.
4. **Die Zerlegung ist die eigentliche Kompetenz.** Nicht das Prompting selbst, sondern die Fähigkeit, einen Task sinnvoll zu zerlegen, bestimmt die Qualität — das wird im Experiment unsichtbar mitgemessen.
5. **Tests müssen tatsächlich existieren, nicht nur möglich sein.** Der Claim "testbarer" erfordert mehr als exportierte Funktionen — er erfordert Tests, die laufen.

## Alternative Sinnachse

Die interessantere Frage ist nicht „Welche Strategie ist besser?" sondern „Ab welcher Komplexität kippt Single-Shot von effizient zu epistemisch teuer?"

Eine Decision Rule wäre wertvoller als ein pauschales Verdict:

| Task-Komplexität | Empfohlene Strategie |
| ---------------- | -------------------- |
| Einfach / trivial | Single-Shot |
| Mittel | Incremental Refinement |
| Hoch / kritisch | Spec-First + Incremental + Tests |

Das verschiebt den Fokus von Technik-Ranking zu Strategie-Selektion nach Task-Klasse.

## Nächste Schritte

- Echte Tests pro Task ergänzen (mindestens Smoke-Tests, besser Unit-Tests)
- Laufzeitvalidierung: Code tatsächlich ausführen, nicht nur kompilieren
- Anforderungsmatrix: erfüllt / teilweise / nicht erfüllt pro Task
- Gemessene Nacharbeit in Patch-Zeilen statt Schätzung
- Replikation mit anderem Modell (GPT-4o, Gemini) und/oder menschlichem Experimentator
- Decision Rule statt pauschales Verdict formulieren
- Kombinationsexperiment: Spec-First + Incremental Refinement

