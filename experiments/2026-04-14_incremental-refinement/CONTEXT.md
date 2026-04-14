---
title: "Incremental Refinement vs. Single-Shot — Kontext"
status: inconclusive
canonicality: operative
---

# CONTEXT.md — Experiment-Kontext

## Ausgangslage

Beim Vibe-Coding gibt es zwei grundlegend verschiedene Strategien, Code von einem LLM generieren zu lassen:

1. **Single-Shot:** Der gesamte Task wird in einem einzelnen, möglichst vollständigen Prompt beschrieben. Das LLM generiert den kompletten Code auf einmal.
2. **Incremental Refinement:** Der Task wird in kleine, aufeinander aufbauende Schritte zerlegt. Jeder Schritt wird einzeln promptet, das Ergebnis reviewt und als Kontext für den nächsten Schritt verwendet.

In der Praxis wählen Entwickler oft intuitiv einen Ansatz, ohne die Trade-offs bewusst abzuwägen. Die Vermutung ist, dass Single-Shot bei einfachen Tasks schneller ist, aber bei steigender Komplexität zu mehr Fehlern und Nacharbeit führt — während Incremental Refinement initial langsamer ist, aber strukturell besseren Code produziert.

Das bestehende Spec-First-Experiment (2026-04-08) hat bereits gezeigt, dass Vorarbeit die Codequalität verbessert. Dieses Experiment untersucht eine orthogonale Dimension: nicht *was* vor der Generierung passiert (Spezifikation), sondern *wie* die Generierung selbst strukturiert wird (Granularität der Prompts).

## Umgebung

- **Tools:** GitHub Copilot (Agent-Modus oder Chat)
- **Sprache:** TypeScript / Node.js
- **Projekttyp:** Drei verschiedene Task-Typen (REST-API, CLI-Tool, Middleware-Stack)
- **Modell(e):** Abhängig vom Durchführungszeitpunkt — das jeweils verfügbare Modell wird dokumentiert

## Relevante Vorarbeiten

- `experiments/2026-04-08_spec-first/` — Zeigt, dass strukturierte Vorarbeit die Codequalität verbessert. Dieses Experiment untersucht die Generierungsstrategie, nicht die Vorarbeit.
- `raw-vibes/catalog-candidates.md` — Listet "Incremental Refinement" als Technique-Kandidaten.

## Einschränkungen

- Die optimale Zerlegung in Teilschritte ist nicht standardisiert und kann variieren
- Incremental Refinement bringt implizit mehr menschlichen Review ein, was den Vergleich verzerren kann
- Die Kontextfenster-Nutzung unterscheidet sich: Incremental akkumuliert Kontext über mehrere Turns
