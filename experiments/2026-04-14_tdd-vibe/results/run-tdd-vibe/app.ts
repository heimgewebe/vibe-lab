/**
 * TDD-Vibe Express app.
 * Wired to satisfy the test suite in users.test.ts.
 *
 * Test-Isolations-Hinweis (korrigiert nach Run-Evidenz):
 *   Bei jedem Import dieses Moduls entsteht eine frische Express-Instanz
 *   (`const app = express()`). Der In-Memory-Store in `users.ts` ist jedoch
 *   modulweit und wird zwischen Tests NICHT automatisch zurückgesetzt — solange
 *   Jest das Modul nur einmal lädt (Standardverhalten), teilen sich alle Tests
 *   denselben Zustand.
 *
 *   Saubere Isolation benötigt deshalb genau einen der beiden Pfade:
 *     a) `beforeEach(() => _resetStore())` aus users.ts aufrufen, oder
 *     b) Jest explizit konfigurieren, Module pro Test neu zu laden
 *        (z. B. `jest.resetModules()` + `jest.isolateModules`).
 *
 *   Dieses Artefakt tut aktuell WEDER a) noch b) — das ist genau der Defekt,
 *   der in den 2 roten Paginierungs-Tests sichtbar wird (seed0@test.com
 *   kollidiert über Tests hinweg). Siehe results/evidence.jsonl.
 */

import express, { NextFunction, Request, Response } from "express";
import { usersRouter } from "./users";

const app = express();

// Body parsing
app.use(express.json());

// Routes
app.use("/users", usersRouter);

// 404 — unknown routes
app.use((_req: Request, res: Response) => {
  res.status(404).json({ success: false, error: { message: "Route not found" } });
});

// 500 — unhandled errors
// eslint-disable-next-line @typescript-eslint/no-unused-vars
app.use((err: Error, _req: Request, res: Response, _next: NextFunction) => {
  console.error("[unhandled error]", err);
  res.status(500).json({ success: false, error: { message: "Internal server error" } });
});

export default app;

if (require.main === module) {
  const PORT = process.env.PORT ?? 3000;
  app.listen(PORT, () => console.log(`Listening on :${PORT}`));
}
