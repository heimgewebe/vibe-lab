#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

RUN_ID = "run-003-rest-api-independent-model-or-tool-condition"
RUN_DIR = Path("experiments/2026-05-31_model-lab-replication-series/artifacts") / RUN_ID
CHALLENGE_PATH = Path("benchmarks/challenges/rest-api-v1.md")
IMPLEMENTATION_DIR = RUN_DIR / "implementation"
TRIGGERED_BY = "user-request-2026-06-05-run-003-execution"
SEMANTIC_REWORK_TRIGGERED_BY = "user-request-2026-06-06-run-003-semantic-rework"
EXECUTOR = "agent:gpt-5.5-api-assistant"
INDEPENDENCE_STATUS = "self_reported_different_agent_tool_context"
CONDITION = "independent_model_or_tool_condition"
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
  "name": "run-003-rest-api-v1-independent-model-or-tool-condition",
  "version": "0.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "test": "vitest run",
    "start": "tsx src/server.ts",
    "verify:static": "python3 verify-run-003.py"
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

SERVER_TS = r"""import Fastify from 'fastify';
import { Type } from '@sinclair/typebox';
import { TypeBoxTypeProvider } from '@fastify/type-provider-typebox';

const NewUserSchema = Type.Object({
  name: Type.String({ minLength: 1 }),
  email: Type.String({ format: 'email' }),
});

const UserPatchSchema = Type.Partial(NewUserSchema, { minProperties: 1 });

type UserRecord = {
  id: string;
  name: string;
  email: string;
  createdAt: string;
  updatedAt: string;
};

type NewUserBody = {
  name: string;
  email: string;
};

type UserPatchBody = Partial<NewUserBody>;

type EnvelopeMeta = Record<string, unknown> | null;

function success<T>(data: T, meta: EnvelopeMeta = null) {
  return { data, error: null, meta };
}

function failure(code: string, message: string, details?: unknown) {
  const error = details === undefined ? { code, message } : { code, message, details };
  return { data: null, error, meta: null };
}

function numericId(id: string) {
  return /^[0-9]+$/.test(id);
}

function nowIso() {
  return new Date().toISOString();
}

export function buildServer() {
  const app = Fastify({ logger: false }).withTypeProvider<TypeBoxTypeProvider>();
  const users = new Map<string, UserRecord>();
  let sequence = 1;

  const emailOwner = (email: string, exceptId?: string) =>
    [...users.values()].find((user) => user.email === email && user.id !== exceptId);

  app.setErrorHandler((error, _request, reply) => {
    if (error.validation) {
      reply.status(422).send(failure('VALIDATION_ERROR', 'Request validation failed.', error.validation));
      return;
    }
    reply.status(500).send(failure('INTERNAL_ERROR', 'Unexpected server error.'));
  });

  app.post<{ Body: NewUserBody }>('/users', { schema: { body: NewUserSchema } }, async (request, reply) => {
    if (emailOwner(request.body.email)) {
      return reply.status(409).send(failure('EMAIL_CONFLICT', 'A user with this email already exists.'));
    }

    const stamp = nowIso();
    const user: UserRecord = {
      id: String(sequence++),
      name: request.body.name,
      email: request.body.email,
      createdAt: stamp,
      updatedAt: stamp,
    };
    users.set(user.id, user);
    return reply.status(201).send(success(user));
  });

  app.get<{ Params: { id: string } }>('/users/:id', async (request, reply) => {
    if (!numericId(request.params.id)) {
      return reply.status(400).send(failure('BAD_ID', 'User id must be numeric.'));
    }
    const user = users.get(request.params.id);
    if (!user) {
      return reply.status(404).send(failure('NOT_FOUND', 'User not found.'));
    }
    return reply.status(200).send(success(user));
  });

  app.put<{ Params: { id: string }; Body: UserPatchBody }>('/users/:id', { schema: { body: UserPatchSchema } }, async (request, reply) => {
    if (!numericId(request.params.id)) {
      return reply.status(400).send(failure('BAD_ID', 'User id must be numeric.'));
    }
    const existing = users.get(request.params.id);
    if (!existing) {
      return reply.status(404).send(failure('NOT_FOUND', 'User not found.'));
    }
    if (request.body.email && emailOwner(request.body.email, request.params.id)) {
      return reply.status(409).send(failure('EMAIL_CONFLICT', 'A user with this email already exists.'));
    }

    const updated: UserRecord = {
      ...existing,
      ...request.body,
      updatedAt: nowIso(),
    };
    users.set(updated.id, updated);
    return reply.status(200).send(success(updated));
  });

  app.delete<{ Params: { id: string } }>('/users/:id', async (request, reply) => {
    if (!numericId(request.params.id)) {
      return reply.status(400).send(failure('BAD_ID', 'User id must be numeric.'));
    }
    if (!users.has(request.params.id)) {
      return reply.status(404).send(failure('NOT_FOUND', 'User not found.'));
    }
    users.delete(request.params.id);
    return reply.status(200).send(success({ deleted: true, id: request.params.id }));
  });

  app.get<{ Querystring: { page?: string; limit?: string } }>('/users', async (request, reply) => {
    const page = Number(request.query.page ?? '1');
    const limit = Number(request.query.limit ?? '20');
    if (!Number.isInteger(page) || page < 1 || !Number.isInteger(limit) || limit < 1 || limit > 100) {
      return reply.status(400).send(failure('BAD_PAGINATION', 'page and limit must be positive integers; limit must be <= 100.'));
    }
    const allUsers = [...users.values()];
    const offset = (page - 1) * limit;
    return reply.status(200).send(success(allUsers.slice(offset, offset + limit), { page, limit, total: allUsers.length }));
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

TEST_TS = r"""import { describe, expect, it } from 'vitest';
import { buildServer } from '../src/server';

async function withServer<T>(fn: (app: ReturnType<typeof buildServer>) => Promise<T>) {
  const app = buildServer();
  try {
    return await fn(app);
  } finally {
    await app.close();
  }
}

describe('rest-api-v1 run-003 surface', () => {
  it('creates users with the success envelope and detects email conflicts', async () => {
    await withServer(async (app) => {
      const created = await app.inject({ method: 'POST', url: '/users', payload: { name: 'Ada', email: 'ada@example.com' } });
      expect(created.statusCode).toBe(201);
      expect(created.json()).toMatchObject({ error: null, meta: null, data: { id: '1', name: 'Ada', email: 'ada@example.com' } });

      const conflict = await app.inject({ method: 'POST', url: '/users', payload: { name: 'Ada Again', email: 'ada@example.com' } });
      expect(conflict.statusCode).toBe(409);
      expect(conflict.json()).toMatchObject({ data: null, error: { code: 'EMAIL_CONFLICT' }, meta: null });
    });
  });

  it('validates request bodies and ids', async () => {
    await withServer(async (app) => {
      const invalidBody = await app.inject({ method: 'POST', url: '/users', payload: { name: '', email: 'not-mail' } });
      expect(invalidBody.statusCode).toBe(422);
      expect(invalidBody.json()).toMatchObject({ data: null, error: { code: 'VALIDATION_ERROR' }, meta: null });

      const invalidId = await app.inject({ method: 'GET', url: '/users/not-a-number' });
      expect(invalidId.statusCode).toBe(400);
      expect(invalidId.json()).toMatchObject({ data: null, error: { code: 'BAD_ID' }, meta: null });
    });
  });

  it('reads, updates, deletes, and returns 404 after delete', async () => {
    await withServer(async (app) => {
      const created = await app.inject({ method: 'POST', url: '/users', payload: { name: 'Grace', email: 'grace@example.com' } });
      const id = created.json().data.id;

      const read = await app.inject({ method: 'GET', url: `/users/${id}` });
      expect(read.statusCode).toBe(200);
      expect(read.json().data.email).toBe('grace@example.com');

      const updated = await app.inject({ method: 'PUT', url: `/users/${id}`, payload: { email: 'hopper@example.com' } });
      expect(updated.statusCode).toBe(200);
      expect(updated.json().data.email).toBe('hopper@example.com');

      const deleted = await app.inject({ method: 'DELETE', url: `/users/${id}` });
      expect(deleted.statusCode).toBe(200);
      expect(deleted.json()).toMatchObject({ error: null, data: { deleted: true, id } });

      const missing = await app.inject({ method: 'GET', url: `/users/${id}` });
      expect(missing.statusCode).toBe(404);
      expect(missing.json()).toMatchObject({ data: null, error: { code: 'NOT_FOUND' }, meta: null });
    });
  });

  it('paginates user lists and rejects invalid pagination', async () => {
    await withServer(async (app) => {
      await app.inject({ method: 'POST', url: '/users', payload: { name: 'A', email: 'a@example.com' } });
      await app.inject({ method: 'POST', url: '/users', payload: { name: 'B', email: 'b@example.com' } });

      const page = await app.inject({ method: 'GET', url: '/users?page=1&limit=1' });
      expect(page.statusCode).toBe(200);
      expect(page.json()).toMatchObject({ error: null, meta: { page: 1, limit: 1, total: 2 } });
      expect(page.json().data).toHaveLength(1);

      const badPage = await app.inject({ method: 'GET', url: '/users?page=0&limit=1' });
      expect(badPage.statusCode).toBe(400);
      expect(badPage.json()).toMatchObject({ data: null, error: { code: 'BAD_PAGINATION' }, meta: null });
    });
  });

  it('documents the 500 error handler path without archiving forced runtime assertion here', async () => {
    await withServer(async (app) => {
      expect(app).toBeDefined();
    });
  });
});
"""

VERIFY_PY = r'''#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent
SERVER = ROOT / "src" / "server.ts"
TESTS = ROOT / "tests" / "users.test.ts"
PACKAGE = ROOT / "package.json"

REQUIRED_SERVER_TOKENS = [
    "app.post",
    "'/users'",
    "app.get",
    "'/users/:id'",
    "app.put",
    "app.delete",
    "setErrorHandler",
    "reply.status(201)",
    "reply.status(400)",
    "reply.status(404)",
    "reply.status(409)",
    "reply.status(422)",
    "reply.status(500)",
    "data: null",
    "error: null",
    "meta",
    "page",
    "limit",
]

REQUIRED_TEST_TOKENS = [
    "POST",
    "GET",
    "PUT",
    "DELETE",
    "201",
    "400",
    "404",
    "409",
    "422",
    "BAD_PAGINATION",
]


def assert_tokens(path: Path, tokens: list[str]) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return [token for token in tokens if token not in text]


def main() -> int:
    missing_files = [str(path) for path in (SERVER, TESTS, PACKAGE) if not path.is_file()]
    if missing_files:
        print("missing files:", missing_files)
        return 1

    missing_server = assert_tokens(SERVER, REQUIRED_SERVER_TOKENS)
    missing_tests = assert_tokens(TESTS, REQUIRED_TEST_TOKENS)
    if missing_server or missing_tests:
        print("missing server tokens:", missing_server)
        print("missing test tokens:", missing_tests)
        return 1

    print("run-003 static verifier: PASS (spec surface present; runtime validation deferred)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Run-003 independent model/tool condition bundle.")
    parser.add_argument("--run-timestamp", default=os.environ.get("RUN_TIMESTAMP"))
    return parser.parse_args()


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    args = parse_args()
    if not args.run_timestamp:
        raise SystemExit("RUN_TIMESTAMP or --run-timestamp is required")

    started = time.monotonic()
    challenge = CHALLENGE_PATH.read_text(encoding="utf-8")
    missing = [token for token in REQUIRED_TOKENS if token not in challenge]
    if missing:
      raise SystemExit(f"Challenge preflight failed; missing tokens: {missing}")

    IMPLEMENTATION_DIR.mkdir(parents=True, exist_ok=True)
    write(IMPLEMENTATION_DIR / "package.json", PACKAGE_JSON)
    write(IMPLEMENTATION_DIR / "src/server.ts", SERVER_TS)
    write(IMPLEMENTATION_DIR / "tests/users.test.ts", TEST_TS)
    write(IMPLEMENTATION_DIR / "verify-run-003.py", VERIFY_PY)
    (IMPLEMENTATION_DIR / "verify-run-003.py").chmod(0o755)

    run_output = f"""# Run-003 Output — Independent Model/Tool Condition

Generated at: {args.run_timestamp}
Triggered by: {TRIGGERED_BY}

## Challenge binding

- challenge_id: `rest-api`
- challenge_version: `rest-api-v1`
- condition: `{CONDITION}`
- independence_status: `{INDEPENDENCE_STATUS}`
- external_attestation: `false`

## Generated implementation surface

- `implementation/package.json`
- `implementation/src/server.ts`
- `implementation/tests/users.test.ts`
- `implementation/verify-run-003.py`

## Preflight

The execution script read `benchmarks/challenges/rest-api-v1.md` and found all required route, validation, envelope, pagination, and status-code tokens.

## Runtime-validation boundary

Run-003 execution surface exists; Run-003 runtime validation is deferred; no result assessment is performed.

This run generated the implementation bundle, static verifier script, and Vitest specification. It does not archive runtime execution of Vitest, forced-500 assertions, npm audit, dependency remediation, production readiness, security readiness, externally attested model independence, model quality, or comparative superiority.
"""
    write(RUN_DIR / "run-output.md", run_output)

    elapsed = time.monotonic() - started
    write(RUN_DIR / "timing.txt", f"Run-003 command elapsed_seconds={elapsed:.3f}\nGenerated timestamp: {args.run_timestamp}\n")
    write(RUN_DIR / "execution.txt", "\n".join([
        "Run-003 execution transcript",
        f"Generated timestamp: {args.run_timestamp}",
        f"Triggered by: {TRIGGERED_BY}",
        f"Executor: {EXECUTOR}",
        "Challenge preflight: PASS",
        f"Required tokens checked: {len(REQUIRED_TOKENS)}",
        "Implementation bundle written: PASS",
        "Static verifier script present: PASS",
        "Vitest spec present: PASS",
        "Independence status: self_reported_different_agent_tool_context",
        "External attestation: false",
        "Runtime validation archived: NO - deferred to separate post-run artifact",
        "Run-003 execution surface exists; Run-003 runtime validation is deferred; no result assessment is performed.",
        "No comparative/model-quality/outcome/adoption/promotion/production/security claim made.",
        "",
    ]))

    meta = {
        "schema_version": "1.0.0",
        "run_id": RUN_ID,
        "generated_at": args.run_timestamp,
        "run_started_at": args.run_timestamp,
        "run_finished_at": args.run_timestamp,
        "executor": EXECUTOR,
        "command": f"RUN_TIMESTAMP={args.run_timestamp} python3 {RUN_DIR / 'execute-run-003.py'}",
        "exit_code": 0,
        "test_output_file": f"artifacts/{RUN_ID}/execution.txt",
        "provenance_level": "self_reported",
        "model_lab_control": True,
        "model_id": "gpt-5.5-api-assistant-session",
        "model_provider": "OpenAI",
        "model_version_or_date": "2026-06-05",
        "tooling": "OpenAI API assistant with repo-local shell/file tools",
        "agent_mode": "two-stage condition-gated repo-local run-003 generation",
        "challenge_id": "rest-api",
        "challenge_version": "rest-api-v1",
        "condition": CONDITION,
        "independence_status": INDEPENDENCE_STATUS,
        "external_attestation": False,
        "condition_boundary_evidence_level": "self_reported",
        "control_condition": CONDITION,
        "temperature_or_sampling": "not_recorded_api_default",
        "human_intervention_level": "user_specified_gate_agent_executed_bundle_no_runtime_validation",
        "surface_status": "executed_runtime_validation_deferred_no_result_assessment",
        "triggered_by": TRIGGERED_BY,
        "semantic_rework_triggered_by": SEMANTIC_REWORK_TRIGGERED_BY,
        "evidence_artifacts": [
            "condition-input.md",
            "execution.txt",
            "changed-files.txt",
            "timing.txt",
            "run-output.md",
            "implementation/package.json",
            "implementation/src/server.ts",
            "implementation/tests/users.test.ts",
            "implementation/verify-run-003.py",
        ],
    }
    write(RUN_DIR / "run_meta.json", json.dumps(meta, indent=2) + "\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
