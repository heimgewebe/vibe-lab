/**
 * TDD-Vibe: tests written FIRST, before any implementation.
 *
 * Coverage goals:
 *  - All 5 endpoints
 *  - Happy paths (2xx)
 *  - Error paths (4xx / 5xx)
 *  - Input validation failures
 *  - Pagination behaviour
 *
 * Runner: Jest + Supertest
 */

import request from "supertest";
import app from "./app";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const validUser = () => ({ name: "Alice Smith", email: "alice@example.com" });
const validUser2 = () => ({ name: "Bob Jones", email: "bob@example.com" });

/** POST and return the created user body */
async function createUser(payload = validUser()) {
  const res = await request(app).post("/users").send(payload);
  return res;
}

// ---------------------------------------------------------------------------
// POST /users
// ---------------------------------------------------------------------------

describe("POST /users", () => {
  describe("happy path", () => {
    it("201 — creates a user and returns envelope with user data", async () => {
      const res = await createUser();
      expect(res.status).toBe(201);
      expect(res.body.success).toBe(true);
      expect(res.body.data).toMatchObject({
        name: "Alice Smith",
        email: "alice@example.com",
      });
      expect(res.body.data.id).toBeDefined();
      expect(res.body.data.createdAt).toBeDefined();
      expect(res.body.data.updatedAt).toBeDefined();
    });

    it("201 — normalises email to lower-case", async () => {
      const res = await createUser({ name: "Charlie", email: "CHARLIE@Example.COM" });
      expect(res.status).toBe(201);
      expect(res.body.data.email).toBe("charlie@example.com");
    });

    it("201 — trims whitespace from name", async () => {
      const res = await createUser({ name: "  Dana  ", email: "dana@example.com" });
      expect(res.status).toBe(201);
      expect(res.body.data.name).toBe("Dana");
    });
  });

  describe("4xx — validation / conflict", () => {
    it("422 — missing name field", async () => {
      const res = await request(app).post("/users").send({ email: "x@x.com" });
      expect(res.status).toBe(422);
      expect(res.body.success).toBe(false);
      expect(res.body.error.message).toBeDefined();
      expect(res.body.error.details).toEqual(
        expect.arrayContaining([expect.objectContaining({ field: "name" })])
      );
    });

    it("422 — missing email field", async () => {
      const res = await request(app).post("/users").send({ name: "Eve" });
      expect(res.status).toBe(422);
      expect(res.body.success).toBe(false);
      expect(res.body.error.details).toEqual(
        expect.arrayContaining([expect.objectContaining({ field: "email" })])
      );
    });

    it("422 — missing both fields (empty body)", async () => {
      const res = await request(app).post("/users").send({});
      expect(res.status).toBe(422);
      expect(res.body.error.details).toHaveLength(2);
    });

    it("400 — invalid email format", async () => {
      const res = await request(app)
        .post("/users")
        .send({ name: "Frank", email: "not-an-email" });
      expect(res.status).toBe(400);
      expect(res.body.success).toBe(false);
    });

    it("400 — blank name (whitespace only)", async () => {
      const res = await request(app)
        .post("/users")
        .send({ name: "   ", email: "g@g.com" });
      expect(res.status).toBe(400);
      expect(res.body.success).toBe(false);
    });

    it("409 — duplicate email", async () => {
      await createUser({ name: "Harry", email: "harry@example.com" });
      const res = await createUser({ name: "Harry 2", email: "harry@example.com" });
      expect(res.status).toBe(409);
      expect(res.body.success).toBe(false);
    });

    it("409 — duplicate email is case-insensitive", async () => {
      await createUser({ name: "Iris", email: "iris@example.com" });
      const res = await createUser({ name: "Iris 2", email: "IRIS@EXAMPLE.COM" });
      expect(res.status).toBe(409);
    });
  });
});

// ---------------------------------------------------------------------------
// GET /users/:id
// ---------------------------------------------------------------------------

describe("GET /users/:id", () => {
  describe("happy path", () => {
    it("200 — returns the user inside envelope", async () => {
      const created = await createUser(validUser2());
      const id = created.body.data.id;

      const res = await request(app).get(`/users/${id}`);
      expect(res.status).toBe(200);
      expect(res.body.success).toBe(true);
      expect(res.body.data.id).toBe(id);
      expect(res.body.data.email).toBe("bob@example.com");
    });
  });

  describe("4xx", () => {
    it("404 — non-existent id", async () => {
      const res = await request(app).get("/users/999999");
      expect(res.status).toBe(404);
      expect(res.body.success).toBe(false);
      expect(res.body.error.message).toMatch(/not found/i);
    });
  });
});

// ---------------------------------------------------------------------------
// PUT /users/:id
// ---------------------------------------------------------------------------

describe("PUT /users/:id", () => {
  describe("happy path", () => {
    it("200 — updates name only", async () => {
      const created = await createUser({ name: "Jan", email: "jan@example.com" });
      const id = created.body.data.id;

      const res = await request(app).put(`/users/${id}`).send({ name: "Janet" });
      expect(res.status).toBe(200);
      expect(res.body.data.name).toBe("Janet");
      expect(res.body.data.email).toBe("jan@example.com"); // unchanged
    });

    it("200 — updates email only", async () => {
      const created = await createUser({ name: "Karl", email: "karl@example.com" });
      const id = created.body.data.id;

      const res = await request(app).put(`/users/${id}`).send({ email: "karl2@example.com" });
      expect(res.status).toBe(200);
      expect(res.body.data.email).toBe("karl2@example.com");
      expect(res.body.data.name).toBe("Karl"); // unchanged
    });

    it("200 — updates both fields", async () => {
      const created = await createUser({ name: "Lena", email: "lena@example.com" });
      const id = created.body.data.id;

      const res = await request(app)
        .put(`/users/${id}`)
        .send({ name: "Lena Updated", email: "lena.updated@example.com" });
      expect(res.status).toBe(200);
      expect(res.body.data.name).toBe("Lena Updated");
      expect(res.body.data.email).toBe("lena.updated@example.com");
    });

    it("200 — updatedAt changes but createdAt stays the same", async () => {
      const created = await createUser({ name: "Mike", email: "mike@example.com" });
      const id = created.body.data.id;
      const originalCreatedAt = created.body.data.createdAt;

      // Small delay to ensure timestamps differ
      await new Promise((r) => setTimeout(r, 5));

      const res = await request(app).put(`/users/${id}`).send({ name: "Michael" });
      expect(res.status).toBe(200);
      expect(res.body.data.createdAt).toBe(originalCreatedAt);
      expect(res.body.data.updatedAt).not.toBe(originalCreatedAt);
    });
  });

  describe("4xx", () => {
    it("404 — user not found", async () => {
      const res = await request(app).put("/users/999999").send({ name: "Ghost" });
      expect(res.status).toBe(404);
      expect(res.body.success).toBe(false);
    });

    it("422 — empty body (no updatable fields)", async () => {
      const created = await createUser({ name: "Nina", email: "nina@example.com" });
      const id = created.body.data.id;

      const res = await request(app).put(`/users/${id}`).send({});
      expect(res.status).toBe(422);
      expect(res.body.success).toBe(false);
    });

    it("400 — invalid email format on update", async () => {
      const created = await createUser({ name: "Omar", email: "omar@example.com" });
      const id = created.body.data.id;

      const res = await request(app)
        .put(`/users/${id}`)
        .send({ email: "not-an-email" });
      expect(res.status).toBe(400);
      expect(res.body.success).toBe(false);
    });

    it("400 — blank name on update", async () => {
      const created = await createUser({ name: "Petra", email: "petra@example.com" });
      const id = created.body.data.id;

      const res = await request(app).put(`/users/${id}`).send({ name: "  " });
      expect(res.status).toBe(400);
      expect(res.body.success).toBe(false);
    });

    it("409 — email already taken by another user", async () => {
      const u1 = await createUser({ name: "Quinn", email: "quinn@example.com" });
      const u2 = await createUser({ name: "Rachel", email: "rachel@example.com" });
      const id = u2.body.data.id;

      const res = await request(app)
        .put(`/users/${id}`)
        .send({ email: "quinn@example.com" });
      expect(res.status).toBe(409);
      expect(res.body.success).toBe(false);
    });
  });
});

// ---------------------------------------------------------------------------
// DELETE /users/:id
// ---------------------------------------------------------------------------

describe("DELETE /users/:id", () => {
  describe("happy path", () => {
    it("200 — deletes user and returns confirmation", async () => {
      const created = await createUser({ name: "Sam", email: "sam@example.com" });
      const id = created.body.data.id;

      const res = await request(app).delete(`/users/${id}`);
      expect(res.status).toBe(200);
      expect(res.body.success).toBe(true);
      expect(res.body.data.id).toBe(id);
      expect(res.body.data.deleted).toBe(true);
    });

    it("200 — deleted user is no longer retrievable (404)", async () => {
      const created = await createUser({ name: "Tara", email: "tara@example.com" });
      const id = created.body.data.id;

      await request(app).delete(`/users/${id}`);
      const getRes = await request(app).get(`/users/${id}`);
      expect(getRes.status).toBe(404);
    });

    it("200 — email is freed after deletion (can re-register)", async () => {
      const created = await createUser({ name: "Uma", email: "uma@example.com" });
      const id = created.body.data.id;

      await request(app).delete(`/users/${id}`);
      const reCreate = await createUser({ name: "Uma 2", email: "uma@example.com" });
      expect(reCreate.status).toBe(201);
    });
  });

  describe("4xx", () => {
    it("404 — user not found", async () => {
      const res = await request(app).delete("/users/999999");
      expect(res.status).toBe(404);
      expect(res.body.success).toBe(false);
    });

    it("404 — double-delete returns 404 on second attempt", async () => {
      const created = await createUser({ name: "Vera", email: "vera@example.com" });
      const id = created.body.data.id;

      await request(app).delete(`/users/${id}`);
      const res = await request(app).delete(`/users/${id}`);
      expect(res.status).toBe(404);
    });
  });
});

// ---------------------------------------------------------------------------
// GET /users (paginated)
// ---------------------------------------------------------------------------

describe("GET /users", () => {
  /** Seed n users so pagination tests start from a known state */
  async function seedUsers(n: number) {
    const results: string[] = [];
    for (let i = 0; i < n; i++) {
      const r = await createUser({ name: `Seed${i}`, email: `seed${i}@test.com` });
      results.push(r.body.data.id);
    }
    return results;
  }

  describe("happy path", () => {
    it("200 — returns paginated envelope with meta", async () => {
      const res = await request(app).get("/users?page=1&limit=10");
      expect(res.status).toBe(200);
      expect(res.body.success).toBe(true);
      expect(Array.isArray(res.body.data)).toBe(true);
      expect(res.body.meta.pagination).toMatchObject({
        page: 1,
        limit: 10,
      });
    });

    it("200 — defaults page=1 limit=10 when query params absent", async () => {
      const res = await request(app).get("/users");
      expect(res.status).toBe(200);
      expect(res.body.meta.pagination.page).toBe(1);
      expect(res.body.meta.pagination.limit).toBe(10);
    });

    it("200 — returns correct slice for page 2", async () => {
      await seedUsers(15);
      const p1 = await request(app).get("/users?page=1&limit=5");
      const p2 = await request(app).get("/users?page=2&limit=5");

      expect(p1.body.data).toHaveLength(5);
      expect(p2.body.data).toHaveLength(5);

      const p1Ids = p1.body.data.map((u: { id: string }) => u.id);
      const p2Ids = p2.body.data.map((u: { id: string }) => u.id);
      // No overlap between pages
      expect(p1Ids.some((id: string) => p2Ids.includes(id))).toBe(false);
    });

    it("200 — last page may return fewer items", async () => {
      // We have some users already; just request a big page number
      const res = await request(app).get("/users?page=999&limit=10");
      expect(res.status).toBe(200);
      expect(Array.isArray(res.body.data)).toBe(true);
      // Could be 0 items, that is fine — just must not 500
    });

    it("200 — hasNextPage is true when more pages exist", async () => {
      await seedUsers(5);
      const res = await request(app).get("/users?page=1&limit=2");
      expect(res.status).toBe(200);
      expect(res.body.meta.pagination.hasNextPage).toBe(true);
    });

    it("200 — hasPrevPage is false on first page", async () => {
      const res = await request(app).get("/users?page=1&limit=10");
      expect(res.body.meta.pagination.hasPrevPage).toBe(false);
    });

    it("200 — hasPrevPage is true on page 2+", async () => {
      await seedUsers(5);
      const res = await request(app).get("/users?page=2&limit=2");
      expect(res.body.meta.pagination.hasPrevPage).toBe(true);
    });

    it("200 — total and totalPages are present", async () => {
      const res = await request(app).get("/users?page=1&limit=10");
      expect(typeof res.body.meta.pagination.total).toBe("number");
      expect(typeof res.body.meta.pagination.totalPages).toBe("number");
    });
  });

  describe("4xx — invalid query params", () => {
    it("400 — page=0 is invalid", async () => {
      const res = await request(app).get("/users?page=0");
      expect(res.status).toBe(400);
      expect(res.body.success).toBe(false);
    });

    it("400 — page=-1 is invalid", async () => {
      const res = await request(app).get("/users?page=-1");
      expect(res.status).toBe(400);
      expect(res.body.success).toBe(false);
    });

    it("400 — page=abc is invalid", async () => {
      const res = await request(app).get("/users?page=abc");
      expect(res.status).toBe(400);
      expect(res.body.success).toBe(false);
    });

    it("400 — limit=0 is invalid", async () => {
      const res = await request(app).get("/users?limit=0");
      expect(res.status).toBe(400);
      expect(res.body.success).toBe(false);
    });

    it("400 — limit=101 exceeds maximum", async () => {
      const res = await request(app).get("/users?limit=101");
      expect(res.status).toBe(400);
      expect(res.body.success).toBe(false);
    });

    it("400 — limit=abc is invalid", async () => {
      const res = await request(app).get("/users?limit=abc");
      expect(res.status).toBe(400);
      expect(res.body.success).toBe(false);
    });
  });
});
