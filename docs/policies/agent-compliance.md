---
title: "Policy — Agent Compliance"
status: active
canonicality: operative
updated: "2026-05-19"
relations:
  - type: references
    target: ../../AGENTS.md
  - type: references
    target: ../../agent-policy.yaml
  - type: references
    target: ../../.vibe/constraints.yml
  - type: references
    target: ../../.vibe/quality-gates.yml
  - type: references
    target: ../../.vibe/generated-artifacts.yml
  - type: references
    target: ../../CLAUDE.md
  - type: references
    target: ../../GEMINI.md
  - type: references
    target: ../../CONVENTIONS.md
  - type: references
    target: ../../.aider.conf.yml
  - type: references
    target: ../../.claude/settings.json
  - type: references
    target: ../../.claude/hooks/session-start.sh
  - type: references
    target: ../../scripts/agents/check_agent_compliance.py
  - type: references
    target: ../../scripts/agents/hooks/pre-commit
---

# Policy — Agent Compliance

> Diese Policy bündelt die bestehenden bindenden Regeln in eine
> agentenfreundliche Übersicht und beschreibt, **wie** sie durchgesetzt
> werden (Mechanismen, Skripte, Hooks). Sie ersetzt keine kanonische
> Quelle — bei Widersprüchen gilt die referenzierte Quelle.

## Zweck

Agentensysteme (Claude Code, Cursor, Aider, Gemini, GitHub Copilot,
Codex CLI, ...) werden in diesem Repo erwartet. Damit sie die
Steuerungsdokumente nicht versehentlich umgehen, gibt es drei
ineinandergreifende Schichten:

1. **Anker-Dateien** — sorgen dafür, dass jedes verbreitete Agent-Tool
   die Leseordnung beim ersten Tool-Auto-Load findet.
2. **Lokaler Guard** — gibt 2-Sekunden-Feedback auf die zwei häufigsten
   Verstöße, bevor CI startet.
3. **CI-Validierung** — die vollständige Gate-Pipeline in
  `.github/workflows/validate.yml` bleibt der harte Boden. CI testet
  den Guard selbst und ergänzt ihn um spezialisierte Drift- und
  Contract-Checks, führt aber aktuell **keinen allgemeinen**
  `agent-check` gegen den PR-Diff aus.

## Anker-Dateien (Tool-Auto-Load)

| Datei | Zielagent | Inhalt |
|-------|-----------|--------|
| [`AGENTS.md`](../../AGENTS.md) | OpenAI Codex CLI, Anthropic Tools, generisch | **Kanonisch** — Pflicht-Leseordnung |
| [`CLAUDE.md`](../../CLAUDE.md) | Claude Code (Web, Desktop, CLI) | Anker → AGENTS.md |
| [`GEMINI.md`](../../GEMINI.md) | Gemini Code Assist | Anker → AGENTS.md |
| [`CONVENTIONS.md`](../../CONVENTIONS.md) + `.aider.conf.yml` | Aider | Anker + Auto-Load-Liste |
| [`.claude/settings.json`](../../.claude/settings.json) + `.claude/hooks/session-start.sh` | Claude Code SessionStart | Druckt Regelkern beim Session-Start |

**Regel:** Alle Anker außer `AGENTS.md` sind **nicht kanonisch**. Sie
verweisen auf AGENTS.md und dürfen den Regelinhalt zusammenfassen, aber
nicht verändern. Wenn ein Anker veraltet und AGENTS.md widerspricht,
gewinnt AGENTS.md.

## Verbote (Kurzform — siehe AGENTS.md für die volle Liste)

1. **Kanonische Steuerungsdokumente** — nur handgepflegt:
   `repo.meta.yaml`, `AGENTS.md`, `agent-policy.yaml`,
   `.vibe/pr-scope-policy.yml`.
2. **Generierte Artefakte** — niemals manuell editieren: `exports/*`,
   `.cursor/rules/*`, `docs/_generated/*`. Stattdessen Generator laufen
   lassen (`make generate-*`).
3. **Status-Umdeutung von Experimenten** — nur mit belegter Grundlage
   (explizite Aussage im Experiment, Decision-Artefakt, struktureller
   Hinweis).
4. **Promotion ohne Gate** — Labor-Artefakte wechseln nur über das
   Promotion-Gate (`.vibe/quality-gates.yml`) in die Bibliothek.
5. **Konzept-Erfindung** — Agenten ergänzen keine Felder oder Ideen, die
   nicht in den Schemas oder kanonischen Quellen verankert sind.

## Durchsetzungs-Map

Welche Regel wird **wo** geprüft?

| Regel | Lokaler Guard (~2 s) | `make validate` (~150 s) | CI |
|-------|:---:|:---:|:---:|
| Kanonische Steuerungsdokumente unangetastet | ✅ `make agent-check` / `make agent-check-staged` | ⚠️ `agent-check-tests` prüfen den Guard, aber kein direkter Diff-Scan | ⚠️ kein allgemeiner `agent-check`-Diff-Scan; Review/Ownership bleibt Backstop |
| Generierte Artefakte nicht manuell editiert | ✅ `make agent-check` / `make agent-check-staged` | ✅ `validate_generated_artifacts_contract.py` + `validate_export_parity.py` + ⚠️ `agent-check-tests` | ✅ Blocking-Artifact-Drift + spezifische Contract-Checks, aber kein allgemeiner `agent-check`-Diff-Scan |
| Schema-Compliance (Experiment, Catalog, Decision) | — | ✅ `validate_schema.py` | ✅ |
| Frontmatter-Relationen konsistent | — | ✅ `validate_relations.py` | ✅ |
| Promotion-Readiness (Falsifizierbarkeit etc.) | — | ✅ Ratchet | ✅ |
| PR-Scope / Artefakt-Boundary | — | ✅ `validate_pr_scope.py` | ✅ |
| Handoff-Block + Hash | — | ✅ `validate_agent_handoff.py` | ✅ |
| Claim ↔ Evidence | — | ✅ `validate_claim_evidence.py` | ✅ |

## Lokale Schnellprüfung

Vor jedem Commit:

```bash
make agent-check    # 2-Sekunden-Guard: kanonische + generierte Pfade
make agent-check-staged
make validate       # vollständige Validierung (~150 s)
```

Optional einmalig installieren (Pre-Commit-Hook):

```bash
bash scripts/agents/install_hooks.sh
```

Der Hook ruft `make agent-check-staged` auf. Dieses Target kapselt
intern `scripts/agents/check_agent_compliance.py --staged --quiet`.
Der Hook ist **opt-in**. CI testet den Guard derzeit über
`agent-check-tests` und ergänzt ihn um spezialisierte Validatoren,
ersetzt aber nicht dieselbe allgemeine lokale Diff-Prüfung.

## Override-Flags (nur bei legitimen Generator-Outputs)

Der Guard erkennt zwei Override-Flags:

```bash
python3 scripts/agents/check_agent_compliance.py --allow-canonical
python3 scripts/agents/check_agent_compliance.py --allow-generated
```

- `--allow-canonical` ist **nur für Maintainer**. Agenten dürfen dieses
  Flag nicht setzen — Edits an kanonischen Steuerungsdokumenten bleiben
  immer ein Verstoß gegen
  [`.vibe/constraints.yml#canonical-sources-immutable-by-agents`](../../.vibe/constraints.yml).
  Das Flag ist damit ein expliziter Maintainer-Override, kein Agentenpfad.
- `--allow-generated` ist erlaubt, **wenn** der Generator gerade gelaufen
  ist (z. B. `make generate-blocking`) und die Änderung dessen Output
  ist. Wird der Guard ohne Generator-Lauf umgangen, erkennt CI den
  Verstoß spätestens beim Drift-Check.

## Verhalten bei Konflikten

Aus AGENTS.md → „Verhaltensregeln":

> **Abbruch bei Konflikten:** Wenn ein generiertes Artefakt einer
> kanonischen Quelle widerspricht, bricht der Agent ab und meldet den
> Konflikt.

Konkretisiert für diese Policy:

1. **Stopp** — keine Annahme treffen, keine „kleinere" Variante des
   Edits versuchen.
2. **Konflikt benennen** — welche Regel? welche Quelle? welcher Pfad?
   Format: `triggered_by`, `policy`, `action`, `outcome`
   (siehe `agent-policy.yaml:traceability`).
3. **Meldung** — als Issue, PR-Kommentar oder strukturierte Diagnose im
   Agent-Output. Stillschweigen ist keine Option.

## Nicht-Ziele

- Diese Policy ersetzt **nicht** `AGENTS.md` oder `agent-policy.yaml` —
  sie verweist auf sie und macht ihre Durchsetzung nachvollziehbar.
- Sie definiert **keine** neuen Constraints. Neue Constraints gehören
  in `.vibe/constraints.yml` (CODEOWNERS-geschützt).
- Sie ist **keine** Schemavalidierung. Schemas leben in `schemas/` und
  `contracts/`.

## Quellen

- Bindend: [`AGENTS.md`](../../AGENTS.md),
  [`agent-policy.yaml`](../../agent-policy.yaml),
  [`repo.meta.yaml`](../../repo.meta.yaml)
- Operativ: [`.vibe/constraints.yml`](../../.vibe/constraints.yml),
  [`.vibe/quality-gates.yml`](../../.vibe/quality-gates.yml),
  [`.vibe/generated-artifacts.yml`](../../.vibe/generated-artifacts.yml)
- PR-Boundary: [`.vibe/pr-scope-policy.yml`](../../.vibe/pr-scope-policy.yml)
