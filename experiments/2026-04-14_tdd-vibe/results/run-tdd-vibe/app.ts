/**
 * TDD-Vibe Express app.
 * Wired to satisfy the test suite in users.test.ts.
 *
 * Each import of this module creates a FRESH Express instance, which means
 * test isolation works correctly when Jest re-requires the module.
 * The in-memory store in users.ts is module-level, so if tests need
 * per-suite isolation they should call _resetStore() in beforeEach.
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
