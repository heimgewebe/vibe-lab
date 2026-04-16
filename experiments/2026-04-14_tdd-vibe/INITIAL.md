---
title: "TDD-Vibe — Initiale Situation"
status: testing
canonicality: operative
document_role: experiment
---

# INITIAL.md — Initiale Situation

## Initialer Prompt / Setup

Das Experiment wurde über einen Subagent-Aufruf orchestriert. Die tatsächlich
verwendeten Prompts sind unten rekonstruiert — wörtlich, so wie sie an den
Generator-Agent gegangen sind. Wer das Experiment replizieren will, sollte diese
Prompts identisch an Claude claude-sonnet-4-6 (oder ein vergleichbares Modell)
geben.

### Gemeinsame Aufgabenbeschreibung

```
Benchmark: REST-API CRUD v1
- TypeScript / Node.js / Express.js
- Endpoints:
    POST /users
    GET  /users/:id
    PUT  /users/:id
    DELETE /users/:id
    GET  /users    (paginated)
- Requirements: Input validation, consistent response structure
  (envelope pattern), correct HTTP status codes
  (200, 201, 400, 404, 409, 422, 500),
  pagination with `page` and `limit`
```

### Kontrollgruppe (Implementation-First)

```
Generate the complete implementation directly from the description above.
Write all code, no tests needed.
```

→ Erwartetes Output: `users.ts`, `app.ts`.

### Treatmentgruppe (TDD-Vibe) — zweistufig

**Prompt 1 — nur Tests:**
```
First, generate ONLY tests (no implementation code).
The tests should cover:
- All 5 endpoints
- Happy path AND error paths (4xx/5xx)
- Input validation failures
- Pagination behavior
```

→ Erwartetes Output: `users.test.ts`.

**Prompt 2 — Implementierung gegen Tests:**
```
Then, generate the implementation to make those tests pass.
```

→ Erwartetes Output: `users.ts`, `app.ts`, sollte die Test-Suite grün machen.

## Systemkonfiguration

- Claude Code (CLI), Agent-Tool mit subagent-Delegation.
- Keine speziellen System-Prompts über Claude-Code-Default hinaus.
- Node.js 22, Jest 30, ts-jest, Supertest für den späteren Testlauf.
- Ausführungsumgebung für den Testlauf: `results/run-tdd-vibe/`.

## Erwartete Baseline

Ohne TDD-Vibe (= Kontrollgruppe): Funktionierender CRUD-Code, typische Lücken bei
Fehlercodes und Edge Cases. Kein Testartefakt, Korrektheit nur durch Augenschein
oder Nutzung prüfbar.

Mit TDD-Vibe (Treatment): Test-Suite zuerst, Implementierung getrieben von den
Test-Assertions. Erwartet: mehr explizite Fehlerfall-Abdeckung, grüne Test-Suite
beim ersten Durchlauf.

**Tatsächliches Baseline-Ergebnis** (siehe `results/run-tdd-vibe/jest-unfixed.log`):
Die Test-Suite läuft **nicht** beim ersten Durchlauf — Compile-Fehler an 4 Stellen
(Express-5-Typing). Der erwartete Vorteil bei "Rework" tritt also nicht ein.
