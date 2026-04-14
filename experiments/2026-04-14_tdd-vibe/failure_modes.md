---
title: "Failure Modes & Limitations (Template)"
status: inconclusive
canonicality: operative
---

# failure_modes.md — Fehler & Grenzen

## Übersicht bekannter Failure Modes

### Context Window Overflow
- **Beschreibung:** Wenn die generierten Tests zu lang werden, vergisst das Modell beim anschließenden Code-Generieren manchmal den anfänglichen Kontext oder spezifische Anweisungen.
- **Auslöser:** Komplexe Aufgaben mit hunderten Zeilen an Tests in einem einzigen Prompt.
- **Mitigation:** Den Prozess auf zwei Prompts aufteilen (erst Tests generieren, diese verifizieren, dann in einem separaten Prompt den Code gegen die Tests implementieren lassen).

### Over-Mocking
- **Beschreibung:** Das Modell neigt dazu, in den Tests alles wegzumocken, wodurch die Tests wertlos werden (sie testen nur die Mocks).
- **Auslöser:** Abhängigkeiten zu externen Systemen oder komplexen internen Modulen.
- **Mitigation:** Im Prompt explizit anweisen, Integrationstests oder reale Instanzen (soweit möglich) zu verwenden und Mocks zu minimieren.
