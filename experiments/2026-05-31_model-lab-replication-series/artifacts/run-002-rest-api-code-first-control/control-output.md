# Run-002 Control Output — rest-api-v1

Generated at: 2026-06-01T06:15:00Z
Challenge source: `benchmarks/challenges/rest-api-v1.md`
Condition: `code_first_control`

## Scope

This artifact indexes a repo-local control response for the `rest-api-v1` benchmark challenge. The response includes a TypeScript/Fastify implementation shape, validation and error-handling behavior, a repo-local static verifier, and an executable but unexecuted Vitest specification under `implementation/`. It is a second execution surface (control run) under the same challenge version as Run-001, enabling first-order comparability structure. It is not a model-quality verdict, comparative result, outcome upgrade, adoption, promotion, or staleness reactivation.

## Produced implementation bundle

- `implementation/package.json` — Node/TypeScript/Fastify dependency and script surface.
- `implementation/src/server.ts` — CRUD users API with envelope responses, validation schemas, conflict handling, not-found handling, pagination, and error envelope handling.
- `implementation/tests/users.test.ts` — executable but unexecuted Vitest specification for create/read/update/delete/list behavior plus validation, conflict, malformed-id, missing-user, and pagination-error cases.
- `implementation/verify-control.py` — repo-local static verifier for required endpoint/status/verification tokens.

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

This control output is execution evidence for a second execution surface only. It does not establish that the implementation is better, worse, more complete, more valid, or to be preferred over Run-001. It does not authorize a comparative verdict, model-quality claim, outcome upgrade, adoption, promotion, or staleness reactivation. The control run and baseline run together enable a first-order comparability surface; actual comparison remains deferred to later assessment artifacts.
