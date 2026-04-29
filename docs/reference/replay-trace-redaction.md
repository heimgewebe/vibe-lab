---
title: "Referenz: Replay-Trace-Redaction"
status: active
canonicality: operative
relations:
  - type: references
    target: ../../tools/vibe-cli/replay_minimal.py
  - type: references
    target: ../../tools/vibe-cli/test_replay_trace_contract.py
schema_version: "0.1.0"
created: "2026-04-28"
updated: "2026-04-29"
author: "heimgewebe"
tags:
  - reference
  - replay
  - redaction
  - security
---

# Referenz: Replay-Trace-Redaction

## Summary

Fixed critical redaction bugs in replay trace v0.2 output where absolute filesystem paths in `target_files` and `locator` fields were not being sanitized before emission. These fields are now properly redacted to prevent accidental leakage of sensitive local machine paths.

## Problems Fixed

### 1. Incomplete Line Format Support in `_redact_path_like_token()`

Issue: The redaction function only supported colon-style line locators (`:10`, `:10:5`) but not hash-style (`#L10`).

Root cause: The regex pattern for extracting line suffixes was:

```python
r"^(.*?)(:\d+(?::\d+)?)$"
```

This matched only `:line` format, missing the common markdown or VS Code `#Lline` format.

Solution: Extended the regex to support both:

```python
r"^(.*?)(:\d+(?::\d+)?|#L\d+)$"
```

### 2. Missing Redaction in `_build_trace_step_v0_2()`

Issue: Two critical fields were copied directly into trace steps without path sanitization:

- `target_files` (list of file paths)
- `locator` (file locator with optional line info)

Impact: Absolute paths like `/tmp/sensitive/readme.md` and `/tmp/sensitive/readme.md:10` appeared unredacted in v0.2 traces.

Solution: Applied `_redact_absolute_paths_in_string()` to both:

```python
# target_files: redact each path in the list
step["target_files"] = [_redact_absolute_paths_in_string(f) for f in target_files]

# locator: redact the locator string (preserves line suffixes)
step["locator"] = _redact_absolute_paths_in_string(locator)
```

## Changes Made

File: `tools/vibe-cli/replay_minimal.py`

### Change 1: Regex Pattern Expansion

```diff
- match = re.match(r"^(.*?)(:\d+(?::\d+)?)$", token)
+ match = re.match(r"^(.*?)(:\d+(?::\d+)?|#L\d+)$", token)
```

### Change 2: Apply Redaction in v0.2 Step Projection

```diff
- step["target_files"] = target_files
+ step["target_files"] = [_redact_absolute_paths_in_string(f) for f in target_files]

  if command == "write_change":
      locator = record.get("locator")
      if isinstance(locator, str):
-         step["locator"] = locator
+         step["locator"] = _redact_absolute_paths_in_string(locator)
```

## Verification

### Test Coverage

The replay trace contract suite covers:

- absolute `target_files` redaction
- absolute `locator` redaction with `:10`
- absolute `locator` redaction with `#L42`
- preservation of repo-relative `docs/index.md#L42`
- recursive absence of absolute local paths in emitted v0.2 payloads

### Example Redaction Behavior

Before fix:

```json
{
  "target_files": ["/tmp/sensitive/readme.md"],
  "locator": "/tmp/sensitive/readme.md:10"
}
```

After fix:

```json
{
  "target_files": ["<external>/readme.md"],
  "locator": "<external>/readme.md:10"
}
```

Repo-relative paths preserved:

```json
{
  "target_files": ["docs/index.md"],
  "locator": "docs/index.md#L42"
}
```

## Impact Assessment

- Scope: Deterministic, non-mutating redaction logic only
- Breaking changes: None in the v0.2 schema surface
- Security: Prevents accidental sensitive path exposure in logs and exports
- Compatibility: Legacy mode remains unaffected

## Next Steps

1. Monitor trace output in downstream consumers for consistency.
2. Extend redaction tests if new path-bearing fields are added to the v0.2 payload.
3. Keep redaction behavior documented alongside replay trace references.