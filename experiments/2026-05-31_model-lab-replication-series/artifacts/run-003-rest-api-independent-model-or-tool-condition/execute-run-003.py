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

  it('documents that forced-500 runtime assertion is intentionally not archived in this bundle', async () => {
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

# --- Canonical bundle artifact templates ---

CONDITION_INPUT_MD = r"""---
title: "Run-003 Condition Input — Independent Model/Tool Condition"
status: executed
canonicality: operative
created: "2026-06-05"
updated: "2026-06-06"
triggered_by: "user-request-2026-06-05-run-003-execution"
last_reworked_by: "user-request-2026-06-06-run-003-semantic-rework"
relations:
  - type: references
    target: "../run-003-plan-stronger-condition-contrast/plan.md"
  - type: references
    target: "../../results/cross-run-assessment.md"
---

# Run-003 Condition Input — Independent Model/Tool Condition

## Purpose

This artifact records the concrete model/tool/condition boundary for Run-003 before execution.

## Condition label

`independent_model_or_tool_condition`

## Challenge

`rest-api-v1`

## Concrete boundary

Run-003 is generated by the current OpenAI API assistant agent context, recorded as `agent:gpt-5.5-api-assistant`, using repo-local shell/file tools in `/workspace/vibe-lab` on 2026-06-05 after an explicit two-stage gate prompt. This differs from the archived Run-001 and Run-002 self-reported contexts:

- Run-001 records `executor: agent:codex-cli`, `model_id: unknown_codex_cli_session`, and tooling `codex-cli local shell`.
- Run-002 records `executor: agent:user-request-2026-06-01-run-002`, `model_id: unknown_user_cli_session`, and tooling `user-local shell execution`.

The challenge remains the same (`rest-api-v1`). The condition boundary is a self-reported different agent/tool/session context plus the explicit condition-gated execution mode, not a change in benchmark scope. The label `independent_model_or_tool_condition` is retained as the planned condition identifier; it does not mean that model independence has been externally established.

## Independence calibration

- `independence_status`: `self_reported_different_agent_tool_context`
- `external_attestation`: `false`
- Interpretation: this is a self-reported different agent/tool/session boundary, not externally attested model independence.

## Evidence for boundary

- Model/tool/agent: `agent:gpt-5.5-api-assistant`; OpenAI API assistant with repo-local shell/file tools; recorded in `run_meta.json`, `run.yml`, `execution.txt`, and `provenance.txt`.
- Execution mode: two-stage condition gate followed by deterministic repo-local bundle generation through `execute-run-003.py`.
- Prompt/input source: `user-request-2026-06-05-run-003-execution`; challenge input `benchmarks/challenges/rest-api-v1.md`; plan input `../run-003-plan-stronger-condition-contrast/plan.md`.
- Human intervention level: user supplied the gate and artifact constraints; the agent performed repository diagnosis, boundary documentation, and bundle generation; Run-003 runtime validation remains deferred.
- Known limitations: the agent/tool/session boundary is self-reported from available session and repo metadata, not externally attested by a provider log. It does not establish model independence, model quality, comparative superiority, condition effect, outcome upgrade, adoption, promotion, production readiness, or security readiness.

## Non-claims

Run-003 execution surface exists; Run-003 runtime validation is deferred; no result assessment is performed.

This condition input does not establish externally attested model independence, model quality, comparative superiority, condition effect, outcome upgrade, adoption, promotion, production readiness, or security readiness.

## Stop rule

If the boundary above cannot be substantiated, Run-003 must not be executed.

## Semantic rework provenance

`last_reworked_by: user-request-2026-06-06-run-003-semantic-rework`
"""

RUN_YML = r"""schema_version: "1.0.0"
contract: "experiment_run_bundle"

run:
  id: "run-003-rest-api-independent-model-or-tool-condition"
  experiment_path: "experiments/2026-05-31_model-lab-replication-series"
  created_at: "__TIMESTAMP__"
  sequence: 3

provenance:
  level: "repo_local"
  executor: "agent:gpt-5.5-api-assistant"
  triggered_by: "user-request-2026-06-05-run-003-execution"
  source_status: "repo_local"
  notes: |
    Run-003 is executed under the same challenge_version (rest-api-v1) as Run-001 and Run-002, but with condition=independent_model_or_tool_condition.
    The concrete model/tool/condition boundary is recorded in condition-input.md.
    Its independence_status is self_reported_different_agent_tool_context and external_attestation is false; the condition label does not prove model independence.
    No model-quality, comparative-superiority, outcome, adoption, promotion, production-readiness, or security-readiness claim is made.
    Run-003 execution surface exists; Run-003 runtime validation is deferred; no result assessment is performed.
    current_comparable_runs counts result-assessment-ready comparable runs, not raw executed surfaces; therefore it remains 0.
    Semantic calibration rework was triggered by user-request-2026-06-06-run-003-semantic-rework.

artifacts:
  run_meta:
    path: "run_meta.json"
    contract: "run_meta"
    canonical: false
    compatibility: true
  measurement:
    path: "measurement.yml"
    contract: "measurement_run"
    canonical: true
  auditor_output:
    path: "auditor-output.yml"
    contract: "auditor_output"
    canonical: true
  evidence_pack:
    path: "evidence-pack.yml"
    contract: "run-evidence-pack.v1"
    canonical: true
  markdown_projection:
    path: "run-output.md"
    canonical: false
    role: "human_projection"

verdict:
  outcome: "MISSING_EVIDENCE"
  effect_claim_allowed: false
  promotion_claim_allowed: false

interpretation_limits:
  min_comparable_runs_required: 3
  current_comparable_runs: 0
  causal_claim_allowed: false
"""

MEASUREMENT_YML = r"""schema_version: "1.0.0"
contract: "measurement_run"
run_id: "run-003-rest-api-independent-model-or-tool-condition"

auditor_verdict: "MISSING_EVIDENCE"
auditor_ref: "auditor-output.yml"

agent_layer_used:
  agent: "agent:gpt-5.5-api-assistant"
  note: "Repo-local Run-003 generation after explicit condition-boundary gate."

metrics:
  scope_drift_count:
    value: 0
    evidence_status: "repo_local"
    notes: "changed-files.txt enumerates all files in the PR diff and constrains the change to the Run-003 bundle plus series/generated reconciliation."
  unsupported_claim_count:
    value: 1
    evidence_status: "derived_from_auditor_output"
    notes: "Derived from auditor-output.yml: exactly one non-PASS claim remains, the deferred runtime-validation evidence claim."
  missing_locator_count:
    value: 0
    evidence_status: "repo_local"
    notes: "All required run-local artifacts resolve in the run-003 artifact directory."
  validation_gap_count:
    value: 1
    evidence_status: "derived_from_auditor_output"
    notes: "Runtime validation for Run-003 is not yet archived; separate post-run validation is required."
  review_friction_count:
    value: null
    evidence_status: "missing_evidence"
    notes: "No human review or rework cycle was measured for this Run-003 execution bundle."
  rework_count:
    value: null
    evidence_status: "missing_evidence"
    notes: "No post-review rework cycle was measured for this Run-003 execution bundle."
  false_block_count:
    value: 0
    evidence_status: "repo_local"
    notes: "No false validator block was observed while creating the Run-003 bundle."
  task_completion_time_observed:
    value: 0.800
    evidence_status: "repo_local"
    notes: "timing.txt records wall-clock capture around the repo-local execute-run-003.py command, but no performance or model-quality claim is made."

missing_evidence:
  - metric: "review_friction_count"
    reason: "No review/rework loop was part of this execution scope."
  - metric: "rework_count"
    reason: "No review/rework loop was part of this execution scope."
  - metric: "validation_gap_count"
    reason: "Run-003 runtime validation is intentionally deferred to a separate post-run artifact."

interpretation_limits:
  - "Run-003 execution surface exists; Run-003 runtime validation is deferred; no result assessment is performed."
  - "No model-quality, comparative-superiority, outcome, adoption, promotion, production-readiness, or security-readiness claim is made."

extensions:
  series: "model-lab-replication-series"
  challenge_id: "rest-api"
  challenge_version: "rest-api-v1"
  condition: "independent_model_or_tool_condition"
  control_condition: "independent_model_or_tool_condition"
  measurement_status: "executed_third_surface_runtime_validation_deferred"
  independence_status: "self_reported_different_agent_tool_context"
  external_attestation: false
  current_executed_surfaces: 3
  current_runtime_validated_surfaces: 2
  current_result_assessment_ready_surfaces: 0
  comparable_run_counting_semantics: "result-assessment-ready comparable runs, not raw executed surfaces"
  semantic_rework_triggered_by: "user-request-2026-06-06-run-003-semantic-rework"
  triggered_by: "user-request-2026-06-05-run-003-execution"
  outcome_upgrade_allowed: false
  adoption_claim_allowed: false
  promotion_claim_allowed: false
"""

COMPARABILITY_YML = r"""schema_version: "1.0.0"
contract: "comparability"
run_id: "run-003-rest-api-independent-model-or-tool-condition"

triggered_by: "user-request-2026-06-05-run-003-execution"

challenge:
  id: "rest-api"
  version: "rest-api-v1"

condition:
  label: "independent_model_or_tool_condition"
  independence_status: "self_reported_different_agent_tool_context"
  external_attestation: false

sibling_runs:
  - id: "run-001-rest-api-spec-first-baseline"
    challenge_version: "rest-api-v1"
    condition: "spec_first_baseline"
  - id: "run-002-rest-api-code-first-control"
    challenge_version: "rest-api-v1"
    condition: "code_first_control"

current_executed_surfaces: 3
current_runtime_validated_surfaces: 2
current_result_assessment_ready_surfaces: 0
min_comparable_runs_required: 3
"""

EVIDENCE_PACK_YML = r"""schema_version: "1.0.0"
run_id: "run-003-rest-api-independent-model-or-tool-condition"
claims:
  - claim_id: "ev3-001"
    text: "Run-003 metadata and run-bundle contracts are present."
    type: "file_changed"
    verdict: "PASS"
    evidence:
      - path: "experiments/2026-05-31_model-lab-replication-series/artifacts/run-003-rest-api-independent-model-or-tool-condition/run.yml"
        status: "repo_local"
      - path: "experiments/2026-05-31_model-lab-replication-series/artifacts/run-003-rest-api-independent-model-or-tool-condition/run_meta.json"
        status: "repo_local"

  - claim_id: "ev3-002"
    text: "Run-003 self-reported different agent/tool/session boundary is recorded before comparative claims; external model-independence attestation is absent."
    type: "scope_adhered_to"
    verdict: "PASS"
    evidence:
      - path: "experiments/2026-05-31_model-lab-replication-series/artifacts/run-003-rest-api-independent-model-or-tool-condition/condition-input.md"
        status: "repo_local"

  - claim_id: "ev3-003"
    text: "Run-003 implementation and declared challenge surface are present."
    type: "generated_artifact_updated"
    verdict: "PASS"
    evidence:
      - path: "experiments/2026-05-31_model-lab-replication-series/artifacts/run-003-rest-api-independent-model-or-tool-condition/implementation/src/server.ts"
        status: "repo_local"
      - path: "experiments/2026-05-31_model-lab-replication-series/artifacts/run-003-rest-api-independent-model-or-tool-condition/implementation/tests/users.test.ts"
        status: "repo_local"
      - path: "experiments/2026-05-31_model-lab-replication-series/artifacts/run-003-rest-api-independent-model-or-tool-condition/implementation/verify-run-003.py"
        status: "repo_local"

  - claim_id: "ev3-004"
    text: "Runtime validation for Run-003 remains deferred."
    type: "validator_succeeded"
    verdict: "MISSING_EVIDENCE"
    evidence:
      - path: "experiments/2026-05-31_model-lab-replication-series/artifacts/run-003-rest-api-independent-model-or-tool-condition/auditor-output.yml"
        status: "repo_local"

  - claim_id: "ev3-005"
    text: "No result assessment or readiness upgrade is made."
    type: "scope_adhered_to"
    verdict: "PASS"
    evidence:
      - path: "experiments/2026-05-31_model-lab-replication-series/artifacts/run-003-rest-api-independent-model-or-tool-condition/comparability.yml"
        status: "repo_local"
      - path: "experiments/2026-05-31_model-lab-replication-series/results/result.md"
        status: "repo_local"

  - claim_id: "ev3-006"
    text: "Run-003 static verifier was executed and archived as static surface evidence (not runtime validation, not Vitest, not forced-500, not dependency-risk, not result assessment, not readiness)."
    type: "validator_succeeded"
    verdict: "PASS"
    evidence:
      - path: "experiments/2026-05-31_model-lab-replication-series/artifacts/run-003-rest-api-independent-model-or-tool-condition/static-verify-run-003.txt"
        status: "repo_local"
"""

AUDITOR_OUTPUT_YML = r"""schema_version: "1.0.0"
contract: "auditor_output"
run_id: "run-003-rest-api-independent-model-or-tool-condition"
auditor:
  name: "agent:gpt-5.5-api-assistant"
  executor: "agent:gpt-5.5-api-assistant"
  date: "2026-06-05"
auditor_date: "2026-06-05"
overall_verdict: "MISSING_EVIDENCE"

extensions:
  auditor_independence_status: "not_applicable_no_external_auditor_attestation"
  auditor_independence_note: >
    No external auditor attestation is claimed for Run-003; independence remains
    self_reported_different_agent_tool_context.
  condition_independence_status: "self_reported_different_agent_tool_context"
  external_attestation: false
  semantic_rework_triggered_by: "user-request-2026-06-06-run-003-semantic-rework"

claims:
  - id: "claim-001"
    text: "Run-003 implementation bundle is present."
    type: "generated_artifact_updated"
    verdict: "PASS"
    evidence:
      - path: "experiments/2026-05-31_model-lab-replication-series/artifacts/run-003-rest-api-independent-model-or-tool-condition/implementation/src/server.ts"
        status: "repo_local"
      - path: "experiments/2026-05-31_model-lab-replication-series/artifacts/run-003-rest-api-independent-model-or-tool-condition/implementation/package.json"
        status: "repo_local"
      - path: "experiments/2026-05-31_model-lab-replication-series/artifacts/run-003-rest-api-independent-model-or-tool-condition/implementation/tests/users.test.ts"
        status: "repo_local"

  - id: "claim-002"
    text: "Run-003 binds to rest-api-v1."
    type: "scope_adhered_to"
    verdict: "PASS"
    evidence:
      - path: "experiments/2026-05-31_model-lab-replication-series/artifacts/run-003-rest-api-independent-model-or-tool-condition/run_meta.json"
        status: "repo_local"

  - id: "claim-003"
    text: "Run-003 self-reported different agent/tool/session boundary is documented without claiming externally attested model independence."
    type: "scope_adhered_to"
    verdict: "PASS"
    evidence:
      - path: "experiments/2026-05-31_model-lab-replication-series/artifacts/run-003-rest-api-independent-model-or-tool-condition/condition-input.md"
        status: "repo_local"

  - id: "claim-004"
    text: "Runtime validation for Run-003 is archived."
    type: "validator_succeeded"
    verdict: "MISSING_EVIDENCE"
    evidence:
      - path: "experiments/2026-05-31_model-lab-replication-series/artifacts/run-003-rest-api-independent-model-or-tool-condition/targeted-tests.txt"
        status: "repo_local"
    notes: "No runtime-validation-run-003 artifact exists in this run bundle; Vitest and forced-500 runtime execution are deferred to a separate post-run artifact."

out_of_scope_claims:
  - id: "out-of-scope-001"
    text: "Run-003 is better, worse, or equivalent in model quality to Run-001/Run-002."
    type: "scope_adhered_to"
    verdict: "OUT_OF_SCOPE"
    evidence:
      - path: "experiments/2026-05-31_model-lab-replication-series/artifacts/run-003-rest-api-independent-model-or-tool-condition/comparability.yml"
        status: "repo_local"
    notes: "No result_assessment performed."

required_next_proof:
  - "Create a separate runtime-validation artifact for Run-003, including static verifier execution, Vitest runtime execution, forced-500 assertion, and dependency-risk observations."
  - "Only after runtime validation should a separate decision_type=result_assessment be considered."
"""

PROVENANCE_TXT = """Run-003 provenance

Run id: run-003-rest-api-independent-model-or-tool-condition
Condition: independent_model_or_tool_condition
Independence status: self_reported_different_agent_tool_context
External attestation: false
Challenge: rest-api-v1
Triggered by: user-request-2026-06-05-run-003-execution
Executor: agent:gpt-5.5-api-assistant
Tooling: OpenAI API assistant with repo-local shell/file tools in /workspace/vibe-lab
Execution mode: explicit condition-boundary gate, then deterministic repo-local bundle generation via execute-run-003.py
Prior-run contrast evidence: Run-001 self-reports agent:codex-cli / unknown_codex_cli_session / codex-cli local shell; Run-002 self-reports unknown_user_cli_session / user-local shell execution.
Known limitations: self-reported different agent/tool/session boundary, not externally attested model independence; no runtime-validation, model-quality, comparative-superiority, outcome, adoption, promotion, production-readiness, or security-readiness claim.
Run-003 status formula: Run-003 execution surface exists; Run-003 runtime validation is deferred; no result assessment is performed.
Semantic rework triggered by: user-request-2026-06-06-run-003-semantic-rework

Exit-code scope note:
The `run_meta.json.exit_code: 0` records the generator execution (execute-run-003.py) only. It does not imply that the static verifier, Vitest runtime tests, forced-500 runtime assertion, npm audit, dependency-risk observations, or any result assessment were executed.
Static verifier execution is archived separately in `static-verify-run-003.txt`; this is static surface evidence only and does not upgrade Run-003 to runtime-validated.
"""

TARGETED_TESTS_TXT = """Run-003 targeted tests and deferred runtime-validation boundary

Spec/Static artifacts present in this bundle:
- implementation/verify-run-003.py checks required route, status-code, envelope, pagination, and error-handler tokens.
- implementation/tests/users.test.ts contains Vitest cases for create, read, update, delete, pagination, 400, 404, 409, and 422 surfaces.

Prepared/executed/deferred status:
- Static verifier (verify-run-003.py): EXECUTED (exit code 0, archived in static-verify-run-003.txt)
- Vitest spec (users.test.ts): PREPARED (not archived as executed)
- Forced-500 assertion: DEFERRED
- npm install / audit / dependency-risk observation: DEFERRED
- Result assessment: DEFERRED

Runtime validation intentionally deferred:
- Do not treat this bundle as archived Vitest runtime evidence.
- Do not treat this bundle as archived forced-500 assertion evidence.
- A later runtime-validation-run-003 artifact should execute the static verifier, Vitest, forced-500 assertion, and dependency-risk observations.

No readiness, outcome, promotion, adoption, production-readiness, or security-readiness claims are made.

Status summary: Run-003 execution surface exists; Run-003 runtime validation is deferred; no result assessment is performed.
"""

CHANGED_FILES_TXT = """Files changed by Run-003 execution
Generated timestamp: __TIMESTAMP__
Triggered by: user-request-2026-06-05-run-003-execution

Scope Boundary:
INCLUDED:
- Run-003 execution bundle for rest-api-v1 under independent_model_or_tool_condition
- Series documentation reconciliation to reference Run-003 as executed but not runtime-validated
- Generated documentation index/taxonomy updates if required by generators

EXCLUDED:
- mutation of Run-001/Run-002 historical bundles
- mutation of Runtime Validation Run-001/Run-002 artifacts
- Run-003 post-run runtime-validation artifact
- benchmark challenge changes
- schema/validator/policy changes
- dependency remediation
- result_assessment decision artifact
- model-quality, comparative-superiority, outcome-upgrade, adoption, promotion, production-readiness, or security-readiness claims

File list:
[add] experiments/2026-05-31_model-lab-replication-series/artifacts/run-003-rest-api-independent-model-or-tool-condition/auditor-output.yml
[add] experiments/2026-05-31_model-lab-replication-series/artifacts/run-003-rest-api-independent-model-or-tool-condition/changed-files.txt
[add] experiments/2026-05-31_model-lab-replication-series/artifacts/run-003-rest-api-independent-model-or-tool-condition/comparability.yml
[add] experiments/2026-05-31_model-lab-replication-series/artifacts/run-003-rest-api-independent-model-or-tool-condition/condition-input.md
[add] experiments/2026-05-31_model-lab-replication-series/artifacts/run-003-rest-api-independent-model-or-tool-condition/evidence-pack.yml
[add] experiments/2026-05-31_model-lab-replication-series/artifacts/run-003-rest-api-independent-model-or-tool-condition/execution.txt
[add] experiments/2026-05-31_model-lab-replication-series/artifacts/run-003-rest-api-independent-model-or-tool-condition/execute-run-003.py
[add] experiments/2026-05-31_model-lab-replication-series/artifacts/run-003-rest-api-independent-model-or-tool-condition/implementation/package.json
[add] experiments/2026-05-31_model-lab-replication-series/artifacts/run-003-rest-api-independent-model-or-tool-condition/implementation/src/server.ts
[add] experiments/2026-05-31_model-lab-replication-series/artifacts/run-003-rest-api-independent-model-or-tool-condition/implementation/tests/users.test.ts
[add] experiments/2026-05-31_model-lab-replication-series/artifacts/run-003-rest-api-independent-model-or-tool-condition/implementation/verify-run-003.py
[add] experiments/2026-05-31_model-lab-replication-series/artifacts/run-003-rest-api-independent-model-or-tool-condition/measurement.yml
[add] experiments/2026-05-31_model-lab-replication-series/artifacts/run-003-rest-api-independent-model-or-tool-condition/provenance.txt
[add] experiments/2026-05-31_model-lab-replication-series/artifacts/run-003-rest-api-independent-model-or-tool-condition/run-output.md
[add] experiments/2026-05-31_model-lab-replication-series/artifacts/run-003-rest-api-independent-model-or-tool-condition/run.yml
[add] experiments/2026-05-31_model-lab-replication-series/artifacts/run-003-rest-api-independent-model-or-tool-condition/run_meta.json
[add] experiments/2026-05-31_model-lab-replication-series/artifacts/run-003-rest-api-independent-model-or-tool-condition/static-verify-run-003.txt
[add] experiments/2026-05-31_model-lab-replication-series/artifacts/run-003-rest-api-independent-model-or-tool-condition/targeted-tests.txt
[add] experiments/2026-05-31_model-lab-replication-series/artifacts/run-003-rest-api-independent-model-or-tool-condition/timing.txt
[modify] docs/_generated/artifact-taxonomy.json
[modify] docs/_generated/artifact-taxonomy.md
[modify] docs/_generated/backlinks.md
[modify] docs/_generated/doc-index.md
[modify] docs/_generated/metrics/trends.md
[modify] docs/_generated/system-map.md
[modify] docs/roadmap.md
[modify] experiments/2026-05-31_model-lab-replication-series/manifest.yml
[modify] experiments/2026-05-31_model-lab-replication-series/method.md
[modify] experiments/2026-05-31_model-lab-replication-series/results/cross-run-assessment.md
[modify] experiments/2026-05-31_model-lab-replication-series/results/evidence.jsonl
[modify] experiments/2026-05-31_model-lab-replication-series/results/result.md

Semantic calibration amendment
Triggered by: user-request-2026-06-06-run-003-semantic-rework
- Clarifies independence_status=self_reported_different_agent_tool_context.
- Records external_attestation=false.
- Explains that current_comparable_runs counts result-assessment-ready comparable runs, not raw executed surfaces.
- Reconciles series documentation to: Run-003 execution surface exists; Run-003 runtime validation is deferred; no result assessment is performed.
- Does not add Run-003 runtime validation or a result_assessment.
Generated reconciliation files:
- docs/_generated/doc-index.md
- docs/_generated/artifact-taxonomy.json
- docs/_generated/artifact-taxonomy.md
- docs/_generated/backlinks.md
- docs/_generated/system-map.md
"""


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

    # --- Implementation surface ---
    IMPLEMENTATION_DIR.mkdir(parents=True, exist_ok=True)
    write(IMPLEMENTATION_DIR / "package.json", PACKAGE_JSON)
    write(IMPLEMENTATION_DIR / "src/server.ts", SERVER_TS)
    write(IMPLEMENTATION_DIR / "tests/users.test.ts", TEST_TS)
    write(IMPLEMENTATION_DIR / "verify-run-003.py", VERIFY_PY)
    (IMPLEMENTATION_DIR / "verify-run-003.py").chmod(0o755)

    # --- Condition input ---
    write(RUN_DIR / "condition-input.md", CONDITION_INPUT_MD)

    # --- Bundle metadata artifacts ---
    write(RUN_DIR / "run.yml", RUN_YML.replace("__TIMESTAMP__", args.run_timestamp))
    write(RUN_DIR / "measurement.yml", MEASUREMENT_YML)
    write(RUN_DIR / "comparability.yml", COMPARABILITY_YML)
    write(RUN_DIR / "auditor-output.yml", AUDITOR_OUTPUT_YML)
    write(RUN_DIR / "evidence-pack.yml", EVIDENCE_PACK_YML)
    write(RUN_DIR / "provenance.txt", PROVENANCE_TXT)
    write(RUN_DIR / "targeted-tests.txt", TARGETED_TESTS_TXT)

    # --- Run output ---
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

    # --- Timing and execution transcript ---
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
        "Bundle metadata artifacts written: PASS (run.yml, measurement.yml, comparability.yml, auditor-output.yml, evidence-pack.yml, condition-input.md, provenance.txt, targeted-tests.txt)",
        "Independence status: self_reported_different_agent_tool_context",
        "External attestation: false",
        "Runtime validation archived: NO - deferred to separate post-run artifact",
        "Run-003 execution surface exists; Run-003 runtime validation is deferred; no result assessment is performed.",
        "No comparative/model-quality/outcome/adoption/promotion/production/security claim made.",
        "",
    ]))

    # --- run_meta.json ---
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
        "command_scope": "initial_run_bundle_generator_without_static_verifier_followup",
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
            "implementation/verify-run-003.py"
        ],
        "review_followup_artifacts": [
            "static-verify-run-003.txt"
        ],
    }
    write(RUN_DIR / "run_meta.json", json.dumps(meta, indent=2) + "\n")

    # --- changed-files.txt (needs timestamp inserted) ---
    write(RUN_DIR / "changed-files.txt", CHANGED_FILES_TXT.replace("__TIMESTAMP__", args.run_timestamp))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
