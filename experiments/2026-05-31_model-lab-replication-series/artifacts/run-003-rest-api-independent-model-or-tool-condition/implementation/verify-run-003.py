#!/usr/bin/env python3
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
