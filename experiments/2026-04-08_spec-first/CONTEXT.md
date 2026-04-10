---
title: "Spec-First Vibe-Coding — Experiment-Kontext"
status: adopted
canonicality: operative
relations:
  - type: informs
    target: ../../catalog/techniques/spec-first-prompting.md
---

# CONTEXT.md — Spec-First Vibe-Coding

## Ausgangslage

Beim Vibe-Coding mit LLM-gestützten Tools wird häufig direkt mit einer vagen Aufgabenstellung gestartet ("Bau mir eine REST-API für Benutzer"). Die Ergebnisse sind oft inkonsistent: Fehlende Felder, unklare Fehlercodes, unvollständige Validierung.

Die Hypothese ist, dass ein vorangestellter Spezifikationsschritt — bei dem das LLM zuerst eine formale Spec (OpenAPI, JSON-Schema o.ä.) generiert und diese vom Menschen reviewt wird, bevor die Implementierung beginnt — die Qualität und Konsistenz des generierten Codes messbar verbessert.

## Umgebung

- **Tools:** VS Code + GitHub Copilot (Chat + Inline)
- **Sprache:** TypeScript / Node.js
- **Projekttyp:** REST-API (Express.js)
- **Modell:** GPT-4o (via Copilot)

## Relevante Vorarbeiten

Keine direkten Vorläufer im Repository. Die Hypothese basiert auf Erfahrungsberichten aus der Vibe-Coding-Community, dass "Spec First" die Prompt-Qualität erhöht.

## Einschränkungen

- Nur ein Modell getestet (GPT-4o via Copilot)
- Subjektive Bewertung des Flows durch einen einzelnen Experimentator
- Kleine Stichprobe (3 Tasks pro Variante)
