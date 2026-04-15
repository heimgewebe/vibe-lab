import { Router, Request, Response } from "express";

export interface User {
  id: string;
  name: string;
  email: string;
  createdAt: string;
  updatedAt: string;
}

// In-memory store (simulates a DB for this benchmark)
const users: Map<string, User> = new Map();
let nextId = 1;

function generateId(): string {
  return String(nextId++);
}

function isValidEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function envelope<T>(data: T, meta?: Record<string, unknown>) {
  return { success: true, data, ...(meta ? { meta } : {}) };
}

function errorEnvelope(message: string, errors?: unknown) {
  return { success: false, error: { message, ...(errors ? { details: errors } : {}) } };
}

export const usersRouter = Router();

// POST /users — Create a user
usersRouter.post("/", (req: Request, res: Response) => {
  const { name, email } = req.body ?? {};

  // 422 — missing or structurally invalid fields
  const missing: string[] = [];
  if (!name) missing.push("name");
  if (!email) missing.push("email");
  if (missing.length > 0) {
    return res.status(422).json(
      errorEnvelope("Missing required fields", missing.map((f) => ({ field: f, message: `${f} is required` })))
    );
  }

  // 400 — semantically invalid value
  if (typeof name !== "string" || name.trim().length === 0) {
    return res.status(400).json(errorEnvelope("name must be a non-empty string"));
  }
  if (typeof email !== "string" || !isValidEmail(email)) {
    return res.status(400).json(errorEnvelope("email must be a valid email address"));
  }

  // 409 — conflict (duplicate email)
  const duplicate = [...users.values()].find((u) => u.email === email.toLowerCase().trim());
  if (duplicate) {
    return res.status(409).json(errorEnvelope("A user with that email already exists"));
  }

  const now = new Date().toISOString();
  const user: User = {
    id: generateId(),
    name: name.trim(),
    email: email.toLowerCase().trim(),
    createdAt: now,
    updatedAt: now,
  };
  users.set(user.id, user);

  return res.status(201).json(envelope(user));
});

// GET /users — List users with pagination
usersRouter.get("/", (req: Request, res: Response) => {
  const rawPage = req.query.page ?? "1";
  const rawLimit = req.query.limit ?? "10";

  const page = parseInt(String(rawPage), 10);
  const limit = parseInt(String(rawLimit), 10);

  if (isNaN(page) || page < 1) {
    return res.status(400).json(errorEnvelope("page must be a positive integer"));
  }
  if (isNaN(limit) || limit < 1 || limit > 100) {
    return res.status(400).json(errorEnvelope("limit must be between 1 and 100"));
  }

  const allUsers = [...users.values()];
  const total = allUsers.length;
  const totalPages = Math.ceil(total / limit) || 1;
  const start = (page - 1) * limit;
  const items = allUsers.slice(start, start + limit);

  return res.status(200).json(
    envelope(items, {
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

// GET /users/:id — Get a single user
usersRouter.get("/:id", (req: Request, res: Response) => {
  const user = users.get(req.params.id);
  if (!user) {
    return res.status(404).json(errorEnvelope(`User with id ${req.params.id} not found`));
  }
  return res.status(200).json(envelope(user));
});

// PUT /users/:id — Update a user
usersRouter.put("/:id", (req: Request, res: Response) => {
  const user = users.get(req.params.id);
  if (!user) {
    return res.status(404).json(errorEnvelope(`User with id ${req.params.id} not found`));
  }

  const { name, email } = req.body ?? {};

  // Must provide at least one field to update
  if (name === undefined && email === undefined) {
    return res.status(422).json(errorEnvelope("Request body must include at least one of: name, email"));
  }

  if (name !== undefined) {
    if (typeof name !== "string" || name.trim().length === 0) {
      return res.status(400).json(errorEnvelope("name must be a non-empty string"));
    }
  }

  if (email !== undefined) {
    if (typeof email !== "string" || !isValidEmail(email)) {
      return res.status(400).json(errorEnvelope("email must be a valid email address"));
    }
    // 409 — email taken by a different user
    const conflict = [...users.values()].find(
      (u) => u.email === email.toLowerCase().trim() && u.id !== user.id
    );
    if (conflict) {
      return res.status(409).json(errorEnvelope("A user with that email already exists"));
    }
  }

  const updated: User = {
    ...user,
    ...(name !== undefined ? { name: name.trim() } : {}),
    ...(email !== undefined ? { email: email.toLowerCase().trim() } : {}),
    updatedAt: new Date().toISOString(),
  };
  users.set(user.id, updated);

  return res.status(200).json(envelope(updated));
});

// DELETE /users/:id — Remove a user
usersRouter.delete("/:id", (req: Request, res: Response) => {
  if (!users.has(req.params.id)) {
    return res.status(404).json(errorEnvelope(`User with id ${req.params.id} not found`));
  }
  users.delete(req.params.id);
  return res.status(200).json(envelope({ id: req.params.id, deleted: true }));
});
