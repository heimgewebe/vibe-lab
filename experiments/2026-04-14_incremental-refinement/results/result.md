---
title: "Incremental Refinement vs. Single-Shot — Ergebnis"
status: testing
canonicality: operative
---

# result.md — Experiment-Ergebnis

## Zusammenfassung

**Incremental Refinement produziert konsistent besseren Code als Single-Shot** — in allen drei Tasks. Die Verbesserungen zeigen sich in Architektur (Modularität), Fehlerbehandlung (strukturierte Fehlerklassen), Typisierung (mehr explizite Interfaces) und Testbarkeit (isoliert testbare Exporte). Der Trade-off: ~6× mehr Prompts und ~2× mehr Code.

Beide Strategien erzeugen kompilierungsfehlerfreien TypeScript-Code (0 Errors in allen 6 Varianten). Der Unterschied liegt nicht in der Korrektheit auf Typ-Ebene, sondern in der **strukturellen Qualität**.

## Beobachtungen

### Wirksamkeit (Effektivität)

| Metrik                     | Single-Shot   | Incremental   | Differenz |
| -------------------------- | ------------- | ------------- | --------- |
| Kompilierungsfehler        | 0/3           | 0/3           | Kein Unterschied |
| Types/Interfaces (Ø)       | 3.3           | 6.7           | +103% |
| Error-Handling-Konstrukte (Ø) | 1.0        | 8.7           | +770% |
| Architektur                | Monolithisch  | Modular       | Qualitativ besser |

**Vollständigkeit:** Incremental-Code deckt mehr Edge Cases ab:
- Task 1: Leere Titel werden validiert, PaginatedResponse hat totalPages-Feld
- Task 2: Unbekannte CLI-Flags werden gemeldet, RegExp-Escape bei Replace
- Task 3: Memory-Leak-Schutz im Rate Limiter (Cleanup-Interval), Request-ID-Tracing

### Reibung (Aufwand)

| Metrik               | Single-Shot | Incremental | Differenz |
| -------------------- | ----------- | ----------- | --------- |
| Prompts pro Task     | 1           | 6           | 6× mehr |
| Dateien pro Task     | 1           | 7           | 7× mehr |
| Ø Zeilen pro Task    | 188         | 402         | 2.1× mehr |
| Geschätzter Rework   | 30–50%      | <10%        | Deutlich weniger |
| Ø Exports pro Task   | 1           | 16          | Massiv testbarer |

**Netto-Aufwand:** Incremental braucht mehr Prompts, spart aber erheblich bei Nacharbeit. Für Produktionscode ist der Trade-off positiv.

### Flow (subjektive Qualität)

| Metrik                     | Single-Shot | Incremental |
| -------------------------- | ----------- | ----------- |
| Code-Lesbarkeit            | 3/5         | 4/5         |
| Architektonische Kohärenz  | 2/5         | 5/5         |
| Vertrauen in Korrektheit   | 3/5         | 4/5         |

**Single-Shot** erzeugt lesbaren, aber unstrukturierten Code. Alles ist "da", aber in einer großen Datei verwoben. Reviews sind mühsamer.

**Incremental** erzeugt Code, der sich "professionell" anfühlt — klare Module, benannte Fehlerklassen, explizite Typen. Der architektonische Zusammenhalt entsteht quasi "von selbst" durch die schrittweise Zerlegung.

## Deutung

Die Hypothese wird **bestätigt**: Incremental Refinement produziert in allen drei Tasks bessere Codequalität bei weniger erwartetem Rework.

**Warum funktioniert es?**
1. **Fokus-Effekt:** Jeder Teilprompt hat einen klar begrenzten Scope. Das LLM kann sich auf eine Sache konzentrieren, statt alles gleichzeitig zu lösen.
2. **Emergente Modularität:** Die Zerlegung in Schritte erzwingt eine Dateitrennung, die automatisch zu Separation of Concerns führt.
3. **Kumulativer Kontext:** Jeder Schritt baut auf dem vorherigen auf. Das LLM "sieht" die bestehenden Typen und Strukturen und passt sich an.
4. **Review-Integration:** Der implizite Review nach jedem Schritt ermöglicht Kurskorrektur — ein Vorteil, der allerdings auch eine Verzerrung darstellt (siehe Einschränkungen).

**Einschränkungen der Deutung:**
- Das Experiment wurde von einem einzelnen Agenten durchgeführt, der beide Strategien simuliert hat. Die "Single-Shot"-Variante wurde bewusst in einem Durchgang geschrieben, die "Incremental"-Variante bewusst schrittweise — aber beides vom selben Modell.
- Die Zerlegung in 6 Schritte ist eine Entscheidung des Experimentators. Andere Zerlegungen könnten andere Ergebnisse liefern.
- Der zusätzliche Review-Schritt in Incremental bringt implizit mehr menschlichen (bzw. Agenten-)Input ein. Reine Prompt-Anzahl ist kein fairer Aufwandsvergleich.

## Verdict

**adopted** — Incremental Refinement wird als Technik für Vibe-Coding-Tasks mittlerer bis hoher Komplexität empfohlen.

Begründung: Klare Verbesserung in 3/3 Tasks bei Architektur, Fehlerbehandlung und Testbarkeit. Der Mehraufwand an Prompts wird durch geringeren Rework kompensiert.

**Einschränkung:** Single-Shot bleibt für Prototypen, einfache Tasks und explorative Code-Generierung sinnvoll. Die Empfehlung ist nicht "immer Incremental", sondern "bewusst wählen".

## Lessons Learned

1. **Modularität ist kein Zufall.** Incremental erzwingt Modularität durch die Zerlegung — das ist ein systemischer Effekt, kein Prompt-Trick.
2. **Fehlerbehandlung profitiert am stärksten.** Der größte Unterschied (770% mehr Error-Handling) zeigt: Single-Shot "vergisst" Fehlerbehandlung, wenn der Prompt zu viel auf einmal verlangt.
3. **Mehr Code ≠ schlechterer Code.** Die ~2× mehr Zeilen bei Incremental sind kein Overhead, sondern explizite Typen, Fehlerklassen und Validierung — alles, was in Single-Shot fehlt.
4. **Die Zerlegung ist die eigentliche Kompetenz.** Nicht das Prompting selbst, sondern die Fähigkeit, einen Task sinnvoll zu zerlegen, bestimmt die Qualität des Incremental-Ansatzes.

## Nächste Schritte

- Catalog-Eintrag für "Incremental Refinement" vorbereiten
- Testen, ob Incremental auch mit anderen Modellen (GPT-4o, Gemini) ähnliche Vorteile zeigt
- Untersuchen, ob es eine optimale Anzahl von Schritten gibt (3? 6? 10?)
- Kombinationsexperiment: Spec-First + Incremental Refinement

