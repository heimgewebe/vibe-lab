#!/usr/bin/env python3
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
    raise SystemExit(f'missing control implementation tokens: {missing}')
print('control implementation static verification passed')
