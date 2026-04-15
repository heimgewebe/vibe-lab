/**
 * TDD-Vibe implementation.
 * Written AFTER the test suite to satisfy every test case.
 */

import { Router, Request, Response } from "express";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface User {
  id: string;
  name: string;
  email: string;
  createdAt: string;
  updatedAt: string;
}

// ---------------------------------------------------------------------------
// In-memory store
// ---------------------------------------------------------------------------

const users: Map<string, User> = new Map();
let _counter = 1;

function generateId(): string {
  return String(_counter++);
}

/** Exposed only for test resets if a beforeEach hook needs it */
export function _resetStore(): void {
  users.clear();
  _counter = 1;
}

// ---------------------------------------------------------------------------
// Utilities
// ---------------------------------------------------------------------------

function isValidEmail(email: unknown): email is string {
  if (typeof email !== "string") return false;
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function normaliseEmail(email: string): string {
  return email.toLowerCase().trim();
}

function normaliseName(name: string): string {
  return name.trim();
}

function isEmailTaken(email: string, excludeId?: string): boolean {
  const norm = normaliseEmail(email);
  for (const u of users.values()) {
    if (u.email === norm && u.id !== excludeId) return true;
  }
  return false;
}

// ---------------------------------------------------------------------------
// Envelope helpers
// ---------------------------------------------------------------------------

type SuccessEnvelope<T> = {
  success: true;
  data: T;
  meta?: Record<string, unknown>;
};

type ErrorEnvelope = {
  success: false;
  error: {
    message: string;
    details?: unknown;
  };
};

function ok<T>(data: T, meta?: Record<string, unknown>): SuccessEnvelope<T> {
  const env: SuccessEnvelope<T> = { success: true, data };
  if (meta !== undefined) env.meta = meta;
  return env;
}

function fail(message: string, details?: unknown): ErrorEnvelope {
  const env: ErrorEnvelope = { success: false, error: { message } };
  if (details !== undefined) env.error.details = details;
  return env;
}

// ---------------------------------------------------------------------------
// Router
// ---------------------------------------------------------------------------

export const usersRouter = Router();

// ---------------------------------------------------------------------------
// POST /users — create a new user
// ---------------------------------------------------------------------------
usersRouter.post("/", (req: Request, res: Response) => {
  const body = req.body ?? {};
  const { name, email } = body;

  // 422 — missing required fields
  const missingFields: { field: string; message: string }[] = [];
  if (name === undefined || name === null || name === "") {
    missingFields.push({ field: "name", message: "name is required" });
  }
  if (email === undefined || email === null || email === "") {
    missingFields.push({ field: "email", message: "email is required" });
  }
  if (missingFields.length > 0) {
    return res.status(422).json(fail("Missing required fields", missingFields));
  }

  // 400 — invalid name (present but blank after trim)
  if (typeof name !== "string" || normaliseName(name).length === 0) {
    return res.status(400).json(fail("name must be a non-empty string"));
  }

  // 400 — invalid email format
  if (!isValidEmail(email)) {
    return res.status(400).json(fail("email must be a valid email address"));
  }

  // 409 — duplicate email
  if (isEmailTaken(email)) {
    return res.status(409).json(fail("A user with that email already exists"));
  }

  const now = new Date().toISOString();
  const user: User = {
    id: generateId(),
    name: normaliseName(name),
    email: normaliseEmail(email),
    createdAt: now,
    updatedAt: now,
  };
  users.set(user.id, user);

  return res.status(201).json(ok(user));
});

// ---------------------------------------------------------------------------
// GET /users — list with pagination
// ---------------------------------------------------------------------------
usersRouter.get("/", (req: Request, res: Response) => {
  const rawPage = (req.query.page as string) ?? "1";
  const rawLimit = (req.query.limit as string) ?? "10";

  const page = parseInt(rawPage, 10);
  const limit = parseInt(rawLimit, 10);

  if (isNaN(page) || page < 1) {
    return res.status(400).json(fail("page must be a positive integer"));
  }
  if (isNaN(limit) || limit < 1 || limit > 100) {
    return res.status(400).json(fail("limit must be an integer between 1 and 100"));
  }

  const all = [...users.values()];
  const total = all.length;
  const totalPages = Math.max(1, Math.ceil(total / limit));
  const start = (page - 1) * limit;
  const data = all.slice(start, start + limit);

  return res.status(200).json(
    ok(data, {
      pagination: {
        page,
        limit,
        total,
        totalPages,
        hasNextPage: page < totalPages,
        hasPrevPage: page > 1,
      },
    })
  );
});

// ---------------------------------------------------------------------------
// GET /users/:id — fetch single user
// ---------------------------------------------------------------------------
usersRouter.get("/:id", (req: Request, res: Response) => {
  const user = users.get(String(req.params.id));
  if (!user) {
    return res.status(404).json(fail(`User with id ${String(req.params.id)} not found`));
  }
  return res.status(200).json(ok(user));
});

// ---------------------------------------------------------------------------
// PUT /users/:id — partial update
// ---------------------------------------------------------------------------
usersRouter.put("/:id", (req: Request, res: Response) => {
  const user = users.get(String(req.params.id));
  if (!user) {
    return res.status(404).json(fail(`User with id ${String(req.params.id)} not found`));
  }

  const body = req.body ?? {};
  const { name, email } = body;
  const hasName = "name" in body;
  const hasEmail = "email" in body;

  // 422 — body contains no recognised updatable fields
  if (!hasName && !hasEmail) {
    return res.status(422).json(fail("Request body must include at least one of: name, email"));
  }

  // 400 — name present but invalid
  if (hasName) {
    if (typeof name !== "string" || normaliseName(name).length === 0) {
      return res.status(400).json(fail("name must be a non-empty string"));
    }
  }

  // 400 / 409 — email present but invalid or taken
  if (hasEmail) {
    if (!isValidEmail(email)) {
      return res.status(400).json(fail("email must be a valid email address"));
    }
    if (isEmailTaken(email, user.id)) {
      return res.status(409).json(fail("A user with that email already exists"));
    }
  }

  const updated: User = {
    ...user,
    ...(hasName ? { name: normaliseName(name as string) } : {}),
    ...(hasEmail ? { email: normaliseEmail(email as string) } : {}),
    updatedAt: new Date().toISOString(),
  };
  users.set(user.id, updated);

  return res.status(200).json(ok(updated));
});

// ---------------------------------------------------------------------------
// DELETE /users/:id
// ---------------------------------------------------------------------------
usersRouter.delete("/:id", (req: Request, res: Response) => {
  if (!users.has(String(req.params.id))) {
    return res.status(404).json(fail(`User with id ${String(req.params.id)} not found`));
  }
  users.delete(String(req.params.id));
  return res.status(200).json(ok({ id: String(req.params.id), deleted: true }));
});
