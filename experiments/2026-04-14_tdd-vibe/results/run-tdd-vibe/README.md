---
title: "TDD-Vibe — Run-Evidenz"
status: testing
canonicality: operative
document_role: experiment
---

# Run-Evidenz — Tatsächlicher Ausführungsnachweis

Dieses Verzeichnis enthält den realen Ausführungsversuch der im `artifacts/tdd-vibe/`
Verzeichnis generierten Test-Suite, sowie zwei kontrastierende Log-Dateien:

## Dateien

- `jest-unfixed.log` — Jest-Lauf gegen die **unveränderten** LLM-Artefakte.
  **Ergebnis: Test Suite failed to run.** TypeScript-Compiler-Fehler an 4 Stellen
  (Express-5-Typing: `req.params.id` ist `string | string[]`, nicht `string`).
  0 von 0 Tests liefen durch — der Code kompiliert nicht.

- `jest-patched.log` — Jest-Lauf gegen eine Kopie mit **minimalem Typ-Fix**
  (`req.params.id` → `String(req.params.id)` an 4 Stellen in `users.ts`).
  **Ergebnis: 38 von 40 Tests grün, 2 rot.** Die 2 Fehler sind Test-Isolations-
  Probleme in der Paginierung (E-Mail-Duplikate über Tests hinweg), weil der
  LLM zwar `_resetStore()` als Abstraktion exportiert hat, die Tests es aber
  nie aufrufen (`grep -n beforeEach users.test.ts` liefert nichts).

- `users.ts`, `app.ts`, `users.test.ts` — patched Kopien; Original unangetastet.
- `package.json`, `package-lock.json`, `tsconfig.json` — Run-Konfiguration.
  Der Lockfile ist **Teil der Run-Evidenz** und bewusst committet: ohne
  exakt eingefrorene Versionen von `ts-jest`, `jest`, `supertest` und
  `express 5.x` ist die Rot-Grün-Evidenz nicht mehr reproduzierbar.
- `node_modules/` — .gitignore'd; wiederherstellbar via `npm ci` (nutzt Lockfile).

## Reproduktion

```
cd results/run-tdd-vibe
npm ci        # nutzt package-lock.json — deterministische Versionen
npx jest
```

## Zwei dadurch gewonnene Evidenz-Punkte

1. **Beide Implementierungen** (impl-first wie tdd-vibe) haben den **gleichen**
   Express-5-Typfehler an strukturell identischen Stellen. Die ursprüngliche
   Annahme „TDD-Vibe produziert weniger manuelle Nacharbeit" ist damit
   **widerlegt** — die Nacharbeit ist bei beiden Ansätzen gleich (4 Patches).

2. **`_resetStore()`** wird im Test nicht verwendet. Die Behauptung
   „Test-First zwingt zu besseren Design-Entscheidungen (Store-Reset)" ist
   optisch zutreffend (die Funktion existiert), funktional aber nicht belegt
   (sie wird nirgendwo aufgerufen, und genau deshalb schlagen 2 Tests fehl).

Beide Befunde kalibrieren die Hauptergebnisse des Experiments nach unten.
