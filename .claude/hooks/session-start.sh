#!/usr/bin/env bash
# .claude/hooks/session-start.sh
# SessionStart hook for Claude Code (Web + Desktop + CLI).
# Surfaces the binding read order and the five core prohibitions
# so every fresh container session starts inside the agent contract.
#
# This file is non-canonical. Source of truth: AGENTS.md.

set -eu

cat <<'EOF'
========================================================================
  Vibe-Lab — Agent Contract (Auto-Surfaced at SessionStart)
========================================================================

Du arbeitest in einem Repo mit bindenden Agentenregeln.
Bevor du irgendetwas tust, lies in dieser Reihenfolge:

  1. repo.meta.yaml         (Repo-Verfassung, kanonisch)
  2. AGENTS.md              (Bindende Leseregeln, kanonisch)
  3. agent-policy.yaml      (Operative Steuerung, kanonisch)
  4. docs/roadmap.md        (Strategischer Kontext)
  5. README.md, docs/index.md
  6. contracts/, schemas/, .vibe/

Bei Widersprüchen gewinnt die höhere Ebene
(canonical > foundational > operative > navigation > diagnosis).

Die fünf Verbote:
  - KEINE Edits an repo.meta.yaml, AGENTS.md, agent-policy.yaml,
    .vibe/pr-scope-policy.yml          (kanonisch, handgepflegt)
  - KEINE manuellen Edits an docs/_generated/*, exports/*,
    .cursor/rules/*                    (generiert, regenerierbar)
  - KEINE Status-Umdeutung von Experimenten ohne Belege
  - KEINE Promotion ohne Promotion-Gate
  - KEINE erfundenen Felder / Konzepte außerhalb Schemas

Vor Commit:
  make agent-check          (2 s — schneller Diff-Guard)
  make validate             (~150 s — vollständiges Gate)

Bei Konflikt: STOPP, melden — nicht raten.
Vollständige Regeln:        AGENTS.md
Compliance-Map:             docs/policies/agent-compliance.md
========================================================================
EOF
