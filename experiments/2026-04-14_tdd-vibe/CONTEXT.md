---
title: "TDD-Vibe — Experiment-Kontext"
status: testing
canonicality: operative
document_role: experiment
---

# CONTEXT.md — TDD-Vibe

## Ausgangslage

Vibe-Coding mit LLMs neigt dazu, Randfälle implizit zu lassen: Das Modell produziert
plausibel aussehenden Code, aber Fehlerpfade werden oft erst bei späterer manueller
Inspektion oder Bugreports sichtbar. Spec-First (Experiment 2026-04-08) adressierte
diesen Mangel, indem ein formales OpenAPI-Artefakt vor der Implementierung generiert
wurde. Spec-First wurde adoptiert.

Die vorliegende Hypothese verschiebt das Artefakt: Statt einer beschreibenden Spec
wird eine **ausführbare Test-Suite** als Voranker genutzt. Der vermutete Mehrwert:
Fehlschläge sind nicht mehr subjektiv einschätzbar, sondern maschinell nachweisbar.

## Umgebung

- **Tools:** Claude Code (CLI), subagent-basiertes Experiment-Setup
- **Sprache:** TypeScript
- **Projekttyp:** REST-API (Express.js)
- **Modell:** Claude claude-sonnet-4-6 (eingeschlossen: claude-opus-4-6 als Reviewer/Kurator)
- **Runner:** Jest + Supertest, Node.js 22 (reale Testausführung unter `results/run-tdd-vibe/`)

## Relevante Vorarbeiten

- `experiments/2026-04-08_spec-first/` — Spec-First mit OpenAPI, adoptiert.
- `raw-vibes/prompt-fragmente.md` — enthält explizit den Impuls
  *"Write the tests for this component first. We will implement the component in the next step."*
- `benchmarks/challenges/rest-api-v1.md` — identische Aufgabenstellung wie im
  Spec-First-Experiment, erlaubt Quervergleich.

## Einschränkungen

- **Ein Modell** (Claude claude-sonnet-4-6). Spec-First wurde mit GPT-4o getestet —
  Modellunterschiede werden damit nicht von Prompting-Unterschieden isoliert.
- **Ein Experimentator** (LLM-Agent). Kein Replikationstest durch unabhängige Session.
- **Asymmetrischer Vergleich:** Kontrollgruppe hat per Anweisung keine Tests — der
  Unterschied "mehr Tests im Treatment" ist konstruktionsbedingt trivial und kein
  Methodeneffekt. Siehe `failure_modes.md`.
- **Ein Benchmark-Task** (REST-API CRUD v1). Keine Aussagen über andere Task-Klassen.
