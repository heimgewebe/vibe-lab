schema_version: "0.1.0"
---
title: "TDD Vibe"
status: adopted
category: style
validated_by:
  - "../../experiments/2026-04-14_tdd-vibe/results/result.md"
---

# TDD Vibe

## Beschreibung
Beim "TDD Vibe" wird das Sprachmodell explizit angewiesen, bei der Code-Generierung zuerst umfassende Tests (inklusive Edge-Cases und Fehler-Handling) zu schreiben, bevor die eigentliche Implementierung generiert wird.

## Kontext & Nutzen
- **Wann einsetzen:** Bei komplexer, isolierter Logik (z.B. Algorithmen, Parser, komplexe Utilities), wo Randbedingungen kritisch sind.
- **Vorteil:** Die Vorab-Generierung von Tests zwingt das Modell, das Problem vollständig zu durchdenken. Dies führt zu signifikant robusterem Code und drastisch weniger Fixing-Iterationen.
- **Nachteil/Einschränkung:** Bei sehr trivialem Code Overhead. Bei sehr großen Dateien besteht die Gefahr, dass das Modell durch die langen Tests den Kontext für die Implementierung verliert.

## Empfohlener Workflow
1. Prompt spezifizieren: "Schreibe ZUERST ausführliche Tests für Funktion X. Erst wenn die Tests vollständig sind, generiere den Code, sodass die Tests grün werden."
2. Tests und Code speichern.
3. Tests ausführen.
4. Bei Fehlschlägen das Modell mit den Fehlermeldungen füttern.
