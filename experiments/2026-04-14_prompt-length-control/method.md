---
title: "Experiment-Methode: Prompt-Length Control"
status: testing
canonicality: operative
relations:
  - type: references
    target: ./metrics.md
---

# method.md — Experiment-Methode

> Beschreibt das strukturierte Vorgehen zur Prüfung der Hypothese.

## Hypothese

Der Leistungszugewinn von Spec/Test-First beruht auf der *inhaltlichen Strukturierung* des Constraints-Raums (Declarative/Executable Mode), nicht lediglich auf dem *Erzwingen einer längeren initialen Output-Generierung* (Token-Bloat als Chain-of-Thought Proxy).

## Methode

1. **Arm 1 (Code-First):** Simuliere den naiven Prompt, der nur auf Code-Ausgabe abzielt. Miss die Edge-Case-Fehler.
2. **Arm 2 (Spec-First):** Fordere das Modell auf, Edge-Cases zu deklarieren, und erst dann Code auszugeben. Miss die Fehler.
3. **Arm 3 (Ramble-First):** Fordere das Modell auf, einen langen, irrelevanten Text zu generieren (Token-Generierung erzwingen), und erst dann Code auszugeben. Miss die Fehler.

### Metriken

- Missed Edge-Cases bei einem komplexen Text-Parsing-Szenario.
- Wenn `Ramble-First` signifikant besser ist als `Code-First`, wäre der Effekt von `Spec-First` nicht primär auf die Struktur, sondern nur auf die Token-Verzögerung (mehr Nachdenkzeit / Kontextaufbau) zurückzuführen.

### Erfolgskriterien

Hypothese bestätigt im Einzelvergleich, falls `Spec-First` in beiden primären Metriken (`test_pass_rate` und `edge_cases_missed`) besser abschneidet als sowohl `Ramble-First` als auch `Code-First` (keine statistische Absicherung, da einzelne Aufgabe ohne Wiederholung — siehe `metrics.md`).

## Confound Isolation

### Konstant gehalten
- **Aufgabe:** Identisches Text-Parsing-Szenario (escaped asterisk) für alle drei Arme
- **Testsuite:** Dieselbe pytest-Testsuite gegen alle generierten Parser
- **Modell:** Gleiches LLM für alle Arme
- **Umgebung:** Gleiche Python/Vibe-Lab-Umgebung

### Variiert
- **Prompt-Strategie:** Code-First (direkt), Spec-First (Edge-Case-Deklaration vor Code), Ramble-First (irrelevante Textgenerierung vor Code)

### Potenzielle Confounds
- **Ramble-Pivot** (dokumentiert in `failure_modes.md`): Das Modell könnte den generierten Ramble-Text implizit zur Strukturierung des Parsing-Problems nutzen, wodurch Ramble-First nicht mehr als reine Token-Bloat-Kontrolle fungiert
- **Aufgabenkomplexität:** Ein einziges Parsing-Szenario könnte zu einfach sein, um Unterschiede zuverlässig zu zeigen

### Nicht kontrollierte Variablen
- **Modell-Varianz zwischen Aufrufen:** Stochastische Unterschiede zwischen einzelnen LLM-Aufrufen (kein Seed/Temperature-Control dokumentiert)
- **Prompt-Formulierung:** Exakte Wortwahl der drei Prompts könnte den Effekt über die Strategie hinaus beeinflussen
- **Reihenfolge der Ausführung:** Nicht dokumentiert, ob die Arme in fester oder randomisierter Reihenfolge ausgeführt wurden
