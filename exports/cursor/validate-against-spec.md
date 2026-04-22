<!-- GENERATED FILE — DO NOT EDIT MANUALLY -->
<!-- source: instruction-blocks/validate-against-spec.md -->
<!-- target-system: cursor -->
<!-- generator: scripts/exports/generate_exports.py -->
<!-- source-hash: 8061256b2d87019356f345a5cb5789f1a0a26d71398854604c6c5229f6b220ba -->

# Validate-Against-Spec
After generating code from a specification:
1. Check every endpoint/function against the spec — are all cases covered?
2. Verify error handling matches the defined error codes
3. Confirm response structures match the schema exactly
4. Test edge cases that were explicitly defined in the spec

If the code deviates from the spec: fix the code, not the spec (unless the spec has a genuine error).
