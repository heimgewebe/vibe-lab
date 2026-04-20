<!-- GENERATED FILE — DO NOT EDIT MANUALLY -->
<!-- source: instruction-blocks/validate-against-spec.md -->
<!-- target-system: copilot -->
<!-- generator: scripts/exports/generate_exports.py -->

# Validate-Against-Spec
After generating code from a specification:
1. Check every endpoint/function against the spec — are all cases covered?
2. Verify error handling matches the defined error codes
3. Confirm response structures match the schema exactly
4. Test edge cases that were explicitly defined in the spec

If the code deviates from the spec: fix the code, not the spec (unless the spec has a genuine error).
