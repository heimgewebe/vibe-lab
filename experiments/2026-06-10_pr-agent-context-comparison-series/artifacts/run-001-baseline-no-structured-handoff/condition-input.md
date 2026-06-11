# Condition Input — Run 001 Baseline: No Structured Handoff

## Condition

`baseline-no-structured-handoff`

## Allowed context

- The user request.
- The PR review comment or task text.
- Any code/diff/log snippets explicitly pasted into the task.
- Autonomous workspace access (opening the repo, viewing the PR diff, inspecting relevant files).
- Using standard development tools (tests, logs, checks).

## Disallowed context

- Vibe-Lab-specific handoff structure.
- Lenskit/repoLens dump or Agent Reading Pack.
- Pre-filled measurement rubric.

## Output request

Ask the agent to solve the PR-review or PR-rework task in the ordinary way.
Do not mention this experiment during execution.

## Boundary

This file defines the condition. It is not a run result.
