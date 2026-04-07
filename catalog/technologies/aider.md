---
name: "Aider"
category: technology
maturity: proven
tools: [aider]
synergies: [incremental-refinement, tdd-vibe, pair-programming-mit-ki]
anti-synergies: []
complexity: medium
speed_boost: "3x"
quality_impact: "++"
tags: [cli, terminal, open-source, git, multi-model]
last_tested: 2026-04-01
---

# 🔧 Aider

## Beschreibung

Aider ist ein **Open-Source Terminal-basierter KI-Coding-Assistent**, der sich durch seine tiefe Git-Integration und Multi-Model-Unterstützung auszeichnet. Jede Änderung wird automatisch als Git-Commit gespeichert.

## Kernfeatures

### Git-Native
- Automatische Commits für jede Änderung
- Saubere Git-History als Nebenprodukt
- Einfaches Rollback durch Git

### Multi-Model Support
- Unterstützt GPT-4, Claude, Gemini, lokale Modelle
- Wechsel zwischen Modellen pro Aufgabe möglich
- Benchmarks für verschiedene Modelle verfügbar

### Repo-Map
- Erstellt automatisch eine Karte des Repositories
- Effizientes Kontext-Management
- Versteht Datei-Beziehungen

## Stärken

- **Open Source** – vollständig transparent und anpassbar
- **Git-Integration** – beste Commit-History aller Tools
- **Multi-Model** – flexibel in der Modellwahl
- **Leichtgewichtig** – schnell installiert und gestartet
- **Repo-Map** – intelligentes Kontext-Management

## Schwächen

- **Terminal-only** – keine IDE-Integration
- **Lernkurve** – viele CLI-Flags und Optionen
- **Weniger mächtig als Cursor Composer** – für Multi-File-Generation
- **Community-maintained** – weniger poliert als kommerzielle Tools

## Best Practices

1. **Dateien gezielt hinzufügen** – nur relevante Dateien in den Chat laden
2. **Architect-Mode für Planung** – erst planen, dann implementieren
3. **Git-History nutzen** – bei Problemen einfach revert
4. **Modell nach Aufgabe wählen** – GPT für Speed, Claude für Reasoning

## Kompatibilität mit Vibe-Stilen

| Stil | Kompatibilität | Stärke |
|------|:--------------:|--------|
| YOLO-Prompting | ⭐⭐⭐ | Schnell, mit Git-Sicherheitsnetz |
| Spec-First Vibe | ⭐⭐⭐⭐ | Architect-Mode |
| TDD-Vibe | ⭐⭐⭐⭐ | Kann Tests ausführen und validieren |
| Pair-Programming | ⭐⭐⭐ | Chat-basiert, eher asynchron |
| Incremental Refinement | ⭐⭐⭐⭐⭐ | Git-Commits pro Schritt |
| Full-Auto Generation | ⭐⭐⭐ | Möglich, aber nicht die Stärke |
