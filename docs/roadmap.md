# vibe-lab: Roadmap

Die Entwicklung von vibe-lab erfolgt in iterativen Phasen. Der Fokus liegt zuerst auf der Etablierung einer stabilen Basis-Artefaktkette, bevor komplexere Subsysteme hinzugefügt werden.

## Phase 1: MVP (Aktuell)
- Etablierung des `.vibe/` Kernmodells (`intent.md`, `constraints.yaml`, `quality-gates.yaml`)
- Minimale Experiment-Struktur (`run.yaml`, `decision.yaml`)
- Basis-Pipeline: Prepare Context -> Generate -> Validate -> Decide
- Initiale Guardrails (Security, Architecture)
- Fokus auf reproduzierbare Runs

## Phase 2: Erweiterung und Messbarkeit
- **Scoring:** Einführung einfacher Metriken (Zeit bis grüne Checks, Rework-Zyklen, Anteil verworfener Outputs). Später Ausbau zum umfassenden "Vibe Score".
- **Context Strategies:** Integration oder Abgrenzung zu bestehenden Kontextmaschinen (z.B. Lenskit/RepoLens). Klärung: Baut `context/` selbst oder evaluiert es nur?
- **Erweiterte Prompt Recipes:** Ausbau der Bibliothek basierend auf Task-Typen (z.B. patch-review, spec-to-tests).

## Phase 3: Skalierung und Kollaboration
- **Collaborative Vibing:** Handoff-Protokolle, Serialisierbarer Session-State, Pair-Vibing Patterns.
- **Meta-Learning:** Automatische Analyse vergangener Sessions, Modell-Profile für verschiedene Aufgaben, Retrospektiven.
- **The Playground:** Dedizierte Sandbox-Umgebungen, Challenge Mode, Speed Runs zum Benchmarken.
