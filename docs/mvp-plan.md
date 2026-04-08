# vibe-lab: MVP Plan

Der MVP fokussiert sich auf eine minimale Artefaktkette, um ein Agent-Experiment reproduzierbar, adoptierbar oder verwerfbar zu machen.

## 1. Das Kernmodell

Die minimale Artefaktkette besteht aus 5 Kerndateien:
- `.vibe/intent.md` (Was soll erreicht werden)
- `.vibe/constraints.yaml` (Technische Grenzen)
- `.vibe/quality-gates.yaml` (Prüfbare Kriterien)
- `experiments/<id>/run.yaml` (Dokumentation des Versuchslaufs)
- `experiments/<id>/decision.yaml` (Ergebnis und nächste Schritte)

## 2. Die Minimalpipeline

Ein vereinfachter Workflow für den Start:
1. **Prepare Context:** Relevante Informationen sammeln.
2. **Generate:** Code erzeugen basierend auf `.vibe/` Verträgen.
3. **Validate:** Test-, Lint- und Security-Checks ausführen.
4. **Decide:** Menschliche/Maschinelle Entscheidung über Übernahme oder Verwerfung.

## 3. Struktur des MVP Repositories

Eine fokussierte, reduzierte Struktur für den Start:

```
vibe-lab/
├── .vibe/
│   ├── intent.md
│   ├── constraints.yaml
│   └── quality-gates.yaml
├── experiments/
│   └── EXP-0001/
│       ├── run.yaml
│       ├── result.md
│       ├── decision.yaml
│       └── evidence.jsonl
├── pipelines/
│   ├── generate/
│   └── validate/
├── guardrails/
│   ├── security/
│   └── architecture/
├── prompts/
│   └── recipes/          # Aufgabentypen statt Buzzwords (z.B. diagnosis, refactor)
├── docs/
│   ├── vision.md
│   ├── mvp-plan.md
│   └── roadmap.md
└── README.md
```

## 4. Tech-Stack (MVP)
- **Core:** TypeScript CLI
- **Konfiguration:** YAML + JSON Schema 2020-12
- **Doku:** Markdown (später VitePress)
- **CI/CD:** GitHub Actions (Wiederverwendbare Workflows)
