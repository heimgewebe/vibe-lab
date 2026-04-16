---
title: "Experiment-Methode: Prompt-Length Control"
status: testing
canonicality: operative
document_role: experiment
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

Hypothese bestätigt, falls `Spec-First` signifikant besser abschneidet als `Ramble-First` und `Code-First`.
