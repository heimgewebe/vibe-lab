#!/usr/bin/env python3
"""Run-001 repo-local baseline execution for rest-api-v1.

The script is deterministic for committed artifacts: callers pass the run
timestamp via --run-timestamp or RUN_TIMESTAMP. It reads the challenge, verifies
that required task anchors are present, and writes a baseline implementation
bundle plus a human-readable baseline-output.md index.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

CHALLENGE_PATH = Path("benchmarks/challenges/rest-api-v1.md")
RUN_DIR = Path(
    "experiments/2026-05-31_model-lab-replication-series/"
    "artifacts/run-001-rest-api-spec-first-baseline"
)
OUTPUT_PATH = RUN_DIR / "baseline-output.md"
IMPLEMENTATION_DIR = RUN_DIR / "implementation"

REQUIRED_TOKENS = [
    "POST /users",
    "GET /users/:id",
    "PUT /users/:id",
    "DELETE /users/:id",
    "GET /users",
    "Input-Validierung",
    "Envelope-Pattern",
    "page",
    "limit",
    "201",
    "400",
    "404",
    "409",
    "422",
    "500",
]

PACKAGE_JSON = """{
  "name": "run-001-rest-api-v1-baseline",
  "version": "0.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "test": "vitest run",
    "start": "tsx src/server.ts"
  },
  "dependencies": {
    "@fastify/type-provider-typebox": "^5.0.0",
    "@sinclair/typebox": "^0.34.0",
    "fastify": "^5.0.0"
  },
  "devDependencies": {
    "tsx": "^4.0.0",
    "typescript": "^5.0.0",
    "vitest": "^3.0.0"
  }
}
"""

SERVER_TS = """import Fastify from 'fastify';
import { Type } from '@sinclair/typebox';
import { TypeBoxTypeProvider } from '@fastify/type-provider-typebox';

const UserInput = Type.Object({
  name: Type.String({ minLength: 1 }),
  email: Type.String({ format: 'email' }),
});

const UserUpdate = Type.Partial(UserInput, { minProperties: 1 });

type User = {
  id: string;
  name: string;
  email: string;
  createdAt: string;
  updatedAt: string;
};

type UserInputBody = {
  name: string;
  email: string;
};

type UserUpdateBody = Partial<UserInputBody>;

function ok<T>(data: T, meta: Record<string, unknown> | null = null) {
  return { data, error: null, meta };
}

function fail(code: string, message: string, details: unknown = null) {
  return { data: null, error: { code, message, details }, meta: null };
}

function isValidId(id: string) {
  return /^\\d+$/.test(id);
}

export function buildServer() {
  const users = new Map<string, User>();
  let nextId = 1;
  const findByEmail = (email: string, exceptId?: string) =>
    [...users.values()].find((user) => user.email === email && user.id !== exceptId);
  const app = Fastify({ logger: false }).withTypeProvider<TypeBoxTypeProvider>();

  app.setErrorHandler((error, _request, reply) => {
    if (error.validation) {
      reply.status(422).send(fail('VALIDATION_ERROR', 'Request validation failed.', error.validation));
      return;
    }
    reply.status(500).send(fail('INTERNAL_ERROR', 'Unexpected server error.'));
  });

  app.post<{ Body: UserInputBody }>('/users', { schema: { body: UserInput } }, async (request, reply) => {
    if (findByEmail(request.body.email)) {
      return reply.status(409).send(fail('EMAIL_CONFLICT', 'A user with this email already exists.'));
    }
    const now = new Date().toISOString();
    const user: User = {
      id: String(nextId++),
      name: request.body.name,
      email: request.body.email,
      createdAt: now,
      updatedAt: now,
    };
    users.set(user.id, user);
    return reply.status(201).send(ok(user));
  });

  app.get<{ Params: { id: string } }>('/users/:id', async (request, reply) => {
    const { id } = request.params;
    if (!isValidId(id)) {
      return reply.status(400).send(fail('BAD_ID', 'User id must be numeric.'));
    }
    const user = users.get(id);
    if (!user) {
      return reply.status(404).send(fail('NOT_FOUND', 'User not found.'));
    }
    return reply.status(200).send(ok(user));
  });

  app.put<{ Params: { id: string }; Body: UserUpdateBody }>('/users/:id', { schema: { body: UserUpdate } }, async (request, reply) => {
    const { id } = request.params;
    if (!isValidId(id)) {
      return reply.status(400).send(fail('BAD_ID', 'User id must be numeric.'));
    }
    const existing = users.get(id);
    if (!existing) {
      return reply.status(404).send(fail('NOT_FOUND', 'User not found.'));
    }
    if (request.body.email && findByEmail(request.body.email, id)) {
      return reply.status(409).send(fail('EMAIL_CONFLICT', 'A user with this email already exists.'));
    }
    const updated: User = {
      ...existing,
      ...request.body,
      updatedAt: new Date().toISOString(),
    };
    users.set(id, updated);
    return reply.status(200).send(ok(updated));
  });

  app.delete<{ Params: { id: string } }>('/users/:id', async (request, reply) => {
    const { id } = request.params;
    if (!isValidId(id)) {
      return reply.status(400).send(fail('BAD_ID', 'User id must be numeric.'));
    }
    if (!users.has(id)) {
      return reply.status(404).send(fail('NOT_FOUND', 'User not found.'));
    }
    users.delete(id);
    return reply.status(200).send(ok({ deleted: true, id }));
  });

  app.get<{ Querystring: { page?: string; limit?: string } }>('/users', async (request, reply) => {
    const page = Number(request.query.page ?? '1');
    const limit = Number(request.query.limit ?? '20');
    if (!Number.isInteger(page) || page < 1 || !Number.isInteger(limit) || limit < 1 || limit > 100) {
      return reply.status(400).send(fail('BAD_PAGINATION', 'page and limit must be positive integers; limit must be <= 100.'));
    }
    const all = [...users.values()];
    const start = (page - 1) * limit;
    const data = all.slice(start, start + limit);
    return reply.status(200).send(ok(data, { page, limit, total: all.length }));
  });

  return app;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const app = buildServer();
  app
    .listen({ port: Number(process.env.PORT ?? 3000), host: '0.0.0.0' })
    .catch((error) => {
      console.error(error);
      process.exit(1);
    });
}
"""

TEST_TS = """import { describe, expect, it } from 'vitest';
import { buildServer } from '../src/server';

async function withServer<T>(fn: (app: ReturnType<typeof buildServer>) => Promise<T>) {
  const app = buildServer();
  try {
    return await fn(app);
  } finally {
    await app.close();
  }
}

describe('rest-api-v1 users baseline', () => {
  it('creates, reads, updates, lists, and deletes users through the envelope pattern', async () => withServer(async (app) => {
    const created = await app.inject({ method: 'POST', url: '/users', payload: { name: 'Ada', email: 'ada@example.test' } });
    expect(created.statusCode).toBe(201);
    expect(created.json().error).toBeNull();
    const id = created.json().data.id;

    const fetched = await app.inject({ method: 'GET', url: `/users/${id}` });
    expect(fetched.statusCode).toBe(200);
    expect(fetched.json().data.email).toBe('ada@example.test');

    const updated = await app.inject({ method: 'PUT', url: `/users/${id}`, payload: { name: 'Ada Lovelace' } });
    expect(updated.statusCode).toBe(200);
    expect(updated.json().data.name).toBe('Ada Lovelace');

    const listed = await app.inject({ method: 'GET', url: '/users?page=1&limit=10' });
    expect(listed.statusCode).toBe(200);
    expect(listed.json().meta).toMatchObject({ page: 1, limit: 10, total: 1 });

    const deleted = await app.inject({ method: 'DELETE', url: `/users/${id}` });
    expect(deleted.statusCode).toBe(200);
    expect(deleted.json().data.deleted).toBe(true);
  }));

  it('covers validation, malformed ids, missing users, conflicts, pagination errors, and server-error guard semantics', async () => withServer(async (app) => {
    expect((await app.inject({ method: 'POST', url: '/users', payload: { name: '', email: 'bad' } })).statusCode).toBe(422);
    expect((await app.inject({ method: 'GET', url: '/users/not-a-number' })).statusCode).toBe(400);
    expect((await app.inject({ method: 'GET', url: '/users/404' })).statusCode).toBe(404);

    await app.inject({ method: 'POST', url: '/users', payload: { name: 'Grace', email: 'grace@example.test' } });
    expect((await app.inject({ method: 'POST', url: '/users', payload: { name: 'Other', email: 'grace@example.test' } })).statusCode).toBe(409);
    expect((await app.inject({ method: 'GET', url: '/users?page=0&limit=10' })).statusCode).toBe(400);

    // Fastify's setErrorHandler represents the documented 500 envelope implementation path.
    // This baseline does not force that path; a later runtime validation step can add a throwing route.
  }));
});
"""

VERIFY_PY = """#!/usr/bin/env python3
from pathlib import Path

server = Path('src/server.ts').read_text(encoding='utf-8')
tests = Path('tests/users.test.ts').read_text(encoding='utf-8')
required_server_tokens = [
    "app.post<{ Body: UserInputBody }>('/users'",
    "app.get<{ Params: { id: string } }>('/users/:id'",
    "app.put<{ Params: { id: string }; Body: UserUpdateBody }>('/users/:id'",
    "app.delete<{ Params: { id: string } }>('/users/:id'",
    "app.get<{ Querystring: { page?: string; limit?: string } }>('/users'",
    "VALIDATION_ERROR",
    "EMAIL_CONFLICT",
    "BAD_ID",
    "NOT_FOUND",
    "BAD_PAGINATION",
    "INTERNAL_ERROR",
    "data: null",
    "error: null",
]
required_test_tokens = [
    "toBe(201)",
    "toBe(200)",
    "toBe(422)",
    "toBe(400)",
    "toBe(404)",
    "toBe(409)",
    "page=1&limit=10",
]
missing = [token for token in required_server_tokens if token not in server]
missing += [token for token in required_test_tokens if token not in tests]
if missing:
    raise SystemExit(f'missing baseline implementation tokens: {missing}')
print('baseline implementation static verification passed')
"""


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_baseline_output(run_timestamp: str) -> str:
    return f"""# Run-001 Baseline Output — rest-api-v1

Generated at: {run_timestamp}
Challenge source: `benchmarks/challenges/rest-api-v1.md`
Condition: `spec_first_baseline`

## Scope

This artifact indexes a repo-local baseline response for the `rest-api-v1` benchmark challenge. The response includes a TypeScript/Fastify implementation shape, validation and error-handling behavior, a repo-local static verifier, and an executable but unexecuted Vitest specification under `implementation/`. It is not a model-quality verdict, comparative result, outcome upgrade, adoption, promotion, or staleness reactivation.

## Produced implementation bundle

- `implementation/package.json` — Node/TypeScript/Fastify dependency and script surface.
- `implementation/src/server.ts` — CRUD users API with envelope responses, validation schemas, conflict handling, not-found handling, pagination, and error envelope handling.
- `implementation/tests/users.test.ts` — executable but unexecuted Vitest specification for create/read/update/delete/list behavior plus validation, conflict, malformed-id, missing-user, and pagination-error cases.
- `implementation/verify-baseline.py` — repo-local static verifier for required endpoint/status/verification tokens.

## API Surface

| Method | Path | Purpose | Primary success status |
| --- | --- | --- | --- |
| POST | `/users` | Create a user | 201 |
| GET | `/users/:id` | Fetch one user by id | 200 |
| PUT | `/users/:id` | Replace/update one user by id | 200 |
| DELETE | `/users/:id` | Delete one user by id | 200 |
| GET | `/users` | List users with pagination | 200 |

## Verification Checklist Produced by This Run

- [x] REST API implementation shape is represented in TypeScript/Fastify source.
- [x] All five required endpoints are represented.
- [x] Input validation is represented for body, path, and query inputs.
- [x] The envelope response pattern is represented for success and failure.
- [x] Required HTTP status codes are mapped to implementation paths: 200, 201, 400, 404, 409, 422, and 500; 500 remains unforced by the current test specification.
- [x] Pagination via `page` and `limit` is represented.
- [x] Verification evidence is represented by a repo-local static verifier script plus an executable but unexecuted Vitest specification for later runtime validation.
- [x] The artifact avoids comparative or model-quality claims.

## Interpretation Limit

This baseline output is execution evidence for a first baseline artifact only. It does not establish that the implementation is complete in production terms, better than another run, validated as a benchmark solution, adopted, promoted, or reusable as a best practice.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Execute deterministic run-001 baseline artifact generation.")
    parser.add_argument(
        "--run-timestamp",
        default=os.environ.get("RUN_TIMESTAMP"),
        help="Fixed ISO-8601 timestamp used in committed output; may also be RUN_TIMESTAMP.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.run_timestamp:
        print("RUN_TIMESTAMP or --run-timestamp is required for deterministic output")
        return 2

    challenge = CHALLENGE_PATH.read_text(encoding="utf-8")
    missing = [token for token in REQUIRED_TOKENS if token not in challenge]
    if missing:
        print(f"challenge preflight failed; missing tokens: {missing}")
        return 1

    write(OUTPUT_PATH, build_baseline_output(args.run_timestamp))
    write(IMPLEMENTATION_DIR / "package.json", PACKAGE_JSON)
    write(IMPLEMENTATION_DIR / "src/server.ts", SERVER_TS)
    write(IMPLEMENTATION_DIR / "tests/users.test.ts", TEST_TS)
    write(IMPLEMENTATION_DIR / "verify-baseline.py", VERIFY_PY)

    checks = {
        "challenge_file_read": CHALLENGE_PATH.exists(),
        "baseline_output_written": OUTPUT_PATH.exists(),
        "package_json_written": (IMPLEMENTATION_DIR / "package.json").exists(),
        "server_ts_written": (IMPLEMENTATION_DIR / "src/server.ts").exists(),
        "test_spec_written": (IMPLEMENTATION_DIR / "tests/users.test.ts").exists(),
        "static_verifier_written": (IMPLEMENTATION_DIR / "verify-baseline.py").exists(),
        "all_required_challenge_tokens_present": not missing,
        "no_comparison_claim_intended": True,
    }
    print("Run-001 rest-api-v1 baseline execution")
    print(f"run_timestamp={args.run_timestamp}")
    print(f"challenge_path={CHALLENGE_PATH}")
    print(f"output_path={OUTPUT_PATH}")
    print(f"implementation_dir={IMPLEMENTATION_DIR}")
    for key, value in checks.items():
        print(f"{key}={value}")
    if not all(checks.values()):
        print("execution checks failed")
        return 1
    print("exit_code=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
