# Repo-Improvement-Audit (2026-05-05)

> Rohe Beobachtung. Keine Promotion. Frei strukturiert.
> Basis: Drei parallele Code-/Schema-/Inhalts-Audits + direkte Inspektion.
> `make validate` läuft fehlerfrei vor und nach den hier vorgeschlagenen
> sicheren Welle-1-Fixes.

## Was funktioniert (kurz)

- Drei-Phasen-Modell ist im Code wirklich umgesetzt: `raw-vibes/` ohne CI,
  `experiments/` mit Schema-Validierung, `catalog/`/`prompts/` mit Promotion-Gate.
- Generated-Artifact-Contract v2 ist operativ (`.vibe/generated-artifacts.yml`,
  `resolve_generated_artifact_paths.py`); CI nutzt die Filter `--ci-policy blocking`
  / `non_blocking` korrekt.
- Promotion-Readiness Ratchet (Phase 2) blockiert neue Verstöße bei stabilem
  Freeze-Korpus. Aktuell 12 Frozen-Cases, alle dokumentiert.
- Replay-Mutation-Guard in CI ist mehrfach abgesichert (Design + Test + CI-Diff).
- PR-Scope-Validator (PR 7) härtet Self-Observation- und Artifact-Boundary-Logik.

## P0 — Tatsächliche Designfehler

### Code-Hygiene

1. **Code-Duplikation: `_extract_frontmatter`** in
   `scripts/adoption/validate_adoption_completeness.py:58–72` reimplementiert
   `_paths.extract_frontmatter`. Driftrisiko (z. B. Fallback-Parser ohne PyYAML
   weicht ab). → Fix: Import aus `_paths`.
2. **Globaler `errors = []` State** in `scripts/docmeta/validate_relations.py:19`
   und `validate_schema.py:66` — verhindert saubere Test-Isolation und ist eine
   versteckte Falle, sobald jemand die Module direkt aus Tests aufruft.
   → Fix für `validate_relations.py` (klein); `validate_schema.py` bewusst
   ausgeklammert (großer Eingriff, viele Funktionen teilen den State).
3. **Mehrfache Definitionen von YAML/Schema-Ladern**: 7 Skripte
   reimplementieren `_load_yaml`/`load_validator`/`build_validator` in leicht
   variierten Formen (`validate_schema.py:115–137`, `validate_run_bundle.py:99–113`,
   `validate_agent_commands.py:49–53`, `validate_command_chain.py:113–117`,
   `validate_agent_handoff.py:90`, `validate_execution_proof.py:48–53`,
   `validate_claim_evidence.py:73–90`). → Fix (außerhalb Welle 1): gemeinsamer
   `_validators.py`. Risiko bei Refactor mittel; verschoben.

### Schemas / Contracts

4. **`schemas/agent.handoff.schema.json` hat kein `schema_version`-Feld**
   — als einziges Schema ohne Versions-Property; Versions-Evolution unmöglich
   ohne breaking change. → Fix: optionales `schema_version` ergänzen
   (kompatibel mit existierenden Fixtures).
5. **`contracts/system_decision.schema.json` hat ebenfalls kein `schema_version`**
   — `additionalProperties: false`, daher Aufnahme erst nach Verifikation
   bestehender Decisions möglich. → Empfehlung: optional ergänzen, sobald die
   beiden bestehenden Decisions in `decisions/system/` aktualisiert sind.
6. **`pr-scope-policy.yml` fehlt in `agent-policy.yaml.read_order` und in der
   AGENTS.md-Liste der handgepflegten Steuerdokumente** — wird vom Validator
   verwendet, aber nicht als Lese-Pflicht für Agenten markiert.
   → Fix: ergänzen.
7. **Verdict-Enum-Reihenfolge** in `schemas/run-evidence-pack.v1.schema.json:57–64`
   weicht von den drei verwandten Schemas (`auditor-output`, `measurement-run`,
   `experiment-run-bundle`) ab — semantisch egal, aber stilistisch inkonsistent
   und erschwert Diff-Reviews. → Fix: angleichen.

### Tests

8. **Keine Tests** für `validate_relations.py`, `validate_execution_proof.py`,
   `validate_schema.py` (außer P2-Counterevidence-Regel). → Fix in Welle 1:
   minimaler Test für `validate_relations.py` (Path-escape, valid, missing target,
   non-list relations). `validate_execution_proof.py` und `validate_schema.py`
   verschoben (umfangreicher).

## P1 — Konsistenz / Lebenszyklus

9. **Frozen-Entries in `.vibe/promotion-readiness-freeze.yml` ohne `expires_at`
   oder `review_date`** — neun Phase-1-Legacy-Einträge mit Begründung
   "pending structured retrofit", aber kein Trigger zum erneuten Prüfen.
   Silent-Rot-Risiko. → Fix in Welle 1: optionales `review_date`-Feld
   dokumentieren (nicht enforced, aber sichtbar).
10. **Status/Decision-Mismatch in einigen Experimenten** (z. B.
    `2026-04-08_spec-first` manifest=`adopted` vs. decision=`mixed`,
    `2026-04-11_yolo-vs-spec-first` manifest=`designed` vs. decision=`not_executed`).
    → Beobachtung dokumentiert; harter Fix erfordert epistemische Klärung,
    nicht nur ein Schema-Feld. Außerhalb dieses Audits.
11. **Catalog-Einträge ohne `last_validated`/`review_cycle`/`next_review_due`**
    (Phase-C-Staleness-Anforderung). Generator `generate_stale_entries.py` ist
    nicht implementiert. → Verschoben (Phase-C-Roadmap).

## P2 — Plan vs. Realität

12. **`docs/foundations/repo-plan.md` Phase C ist veraltet:**
    - "Export-Herkunft (`source_hash`)" als `[ ]` markiert, ist aber implementiert
      (siehe `exports/copilot/spec-first.md` Header). → Fix: auf `[x]`.
    - "Export-Konflikt-Gate" als `[ ]` markiert, ist aber via
      `validate_export_parity.py` (CI-blocking) implementiert. → Fix: auf `[x]`.
13. **Repo-Plan-`updated:`-Tag** ist 2026-04-23, neueste Experimente sind
    2026-05-01. → Klein, aber Plan claims "Teilstand" — sollte aktualisiert
    werden, sobald Phase-C-Punkte konsolidiert sind.

## P2 — Inhalts-Lücken

14. **`docs/onboarding/`** ist leer (nur `.gitkeep`). Phase D, aber 0 Inhalt
    vs. dokumentierte Absicht im Repo-Plan. → Verschoben (eigene Initiative).
15. **`docs/rules/`, `docs/syntheses/`, `docs/experiments/`** leer. → OK,
    solange Plan das spiegelt; sonst Stub-Notiz.
16. **`decisions/benchmark/`, `decisions/export/`, `decisions/policy/`** leer. → OK,
    Stub. Sollte aber irgendwo dokumentiert sein, dass diese Splits absichtlich
    sind (nicht jeder Split braucht initial Inhalt).
17. **`docs/playbooks/plan-execution-checklist.md`** existiert, ist aber nicht
    in `docs/index.md` verlinkt. → Fix in Welle 1: Link ergänzen.
18. **113 Orphan-Dokumente** laut `docs/_generated/orphans.md` — viele davon
    by design (exports, experiment CONTEXT/INITIAL/method). Der Generator könnte
    eine "expected-orphan"-Allowlist nutzen, damit echte Orphans (wie
    `plan-execution-checklist.md` vor Welle 1) sichtbar bleiben. → Verschoben.

## P3 — Refactor-Backlog (nichts hier umgesetzt)

- Gemeinsamer `scripts/docmeta/_validators.py` für Loader / Validator-Bau.
- Logging statt `print()` in allen Validatoren (mit `--quiet` / `--verbose`).
- Einheitliche Exit-Code-Konvention (0 ok / 1 violation / 2 usage) dokumentieren
  und durchsetzen.
- `sys.path.insert`-Pattern durch echtes Package (`scripts/docmeta/__init__.py`
  + relative Imports + `python -m`) ersetzen.

## Welle-1-Fixes (in dieser Session umgesetzt)

| # | Datei | Risiko | Effekt |
|---|-------|--------|--------|
| 1 | `scripts/adoption/validate_adoption_completeness.py` | klein | Codeduplikation entfernt |
| 2 | `scripts/docmeta/validate_relations.py` | klein | Globaler State raus, Test-Isolation gegeben |
| 3 | `schemas/agent.handoff.schema.json` | klein (optional) | Versions-Property nachrüstbar |
| 4 | `agent-policy.yaml` + `AGENTS.md` | trivial | `pr-scope-policy.yml` als kanonisch sichtbar |
| 5 | `schemas/run-evidence-pack.v1.schema.json` | trivial (Stil) | Verdict-Enum-Reihenfolge angleichen |
| 6 | `.vibe/promotion-readiness-freeze.yml` (Doku) | trivial | `review_date`-Feld dokumentiert |
| 7 | `docs/foundations/repo-plan.md` | trivial | Phase-C-Checkboxen synchronisieren |
| 8 | `docs/index.md` | trivial | Playbook `plan-execution-checklist.md` verlinken |
| 9 | `scripts/docmeta/test_validate_relations.py` (neu) | klein | Test für bisher ungetesteten Validator |
