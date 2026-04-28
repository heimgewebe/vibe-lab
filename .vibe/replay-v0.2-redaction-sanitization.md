# Replay v0.2 Redaction Sanitization — Work Complete

**Date:** 2026-04-28  
**Branch:** `claude/replay-v0.2-sanitizing-semantics-follow-up`  
**Commit:** `33d3b20` 

## Summary

Fixed critical redaction bugs in replay trace v0.2 output where absolute filesystem paths in `target_files` and `locator` fields were not being sanitized before emission. These fields are now properly redacted to prevent accidental leakage of sensitive local machine paths.

## Problems Fixed

### 1. Incomplete Line Format Support in `_redact_path_like_token()`

**Issue:** The redaction function only supported colon-style line locators (`:10`, `:10:5`) but not hash-style (`#L10`).

**Root Cause:** The regex pattern for extracting line suffixes was:
```python
r"^(.*?)(:\d+(?::\d+)?)$"
```

This matched only `:line` format, missing the common markdown/vscode `#Lline` format.

**Solution:** Extended the regex to support both:
```python
r"^(.*?)(:\d+(?::\d+)?|#L\d+)$"
```

### 2. Missing Redaction in `_build_trace_step_v0_2()`

**Issue:** Two critical fields were copied directly into trace steps without path sanitization:

- **`target_files`** (list of file paths) — Line 115
- **`locator`** (file locator with optional line info) — Line 119

**Impact:** Absolute paths like `/tmp/sensitive/readme.md` and `/tmp/sensitive/readme.md:10` appeared unredacted in v0.2 traces.

**Solution:** Applied `_redact_absolute_paths_in_string()` to both:

```python
# target_files: redact each path in the list
step["target_files"] = [_redact_absolute_paths_in_string(f) for f in target_files]

# locator: redact the locator string (preserves line suffixes)
step["locator"] = _redact_absolute_paths_in_string(locator)
```

## Changes Made

**File:** `tools/vibe-cli/replay_minimal.py`

### Change 1: Line 213 — Regex Pattern Expansion

```diff
- match = re.match(r"^(.*?)(:\d+(?::\d+)?)$", token)
+ match = re.match(r"^(.*?)(:\d+(?::\d+)?|#L\d+)$", token)
```

### Change 2: Lines 118–121 — Apply Redaction

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

All existing tests continue to pass:

- **Redaction Suite** (newly passing):
  - ✅ `test_absolute_target_files_are_redacted_or_normalized` 
  - ✅ `test_absolute_locator_is_redacted`
  - ✅ `test_v0_2_payload_contains_no_absolute_paths_recursively`

- **Full replay_trace_contract.py suite**: **21/21 tests** ✅
  - Validation, determinism, error handling, legacy compatibility

- **Cross-contract tests**: **14/14 tests** ✅
  - Handoff validation, version conflicts, semantic mismatches

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

- **Scope:** Deterministic, non-mutating redaction logic only
- **Breaking Changes:** None (backward-compatible v0.2 schema)
- **Security:** Prevents accidental sensitive path exposure in logs/exports
- **Compatibility:** All existing tests pass; legacy mode unaffected

## Next Steps

1. Monitor trace output in downstream consumers for consistency
2. Consider extending redaction to other string fields if needed
3. Document redaction behavior in trace schema references
