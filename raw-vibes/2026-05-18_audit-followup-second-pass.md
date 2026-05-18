# Repo-Audit-Followup (2026-05-18) — Second Pass

> Rohe Beobachtung. Keine Promotion. Knüpft an
> `raw-vibes/2026-05-05_repo-improvement-audit.md` an.
> `make validate` läuft vorher und nachher fehlerfrei.

## Status der Welle-1-Fixes (vom 2026-05-05)

| # | Fix | Status | Beleg |
|---|-----|--------|-------|
| 1 | `_extract_frontmatter` aus `_paths` importieren | ✅ | `scripts/adoption/validate_adoption_completeness.py:41` |
| 2 | `validate_relations.py` global state raus | ✅ | `scripts/docmeta/validate_relations.py:20-32` (errors als Parameter) |
| 3 | `schema_version` in `agent.handoff.schema.json` | ✅ | `schemas/agent.handoff.schema.json:8-12` |
| 4 | `pr-scope-policy.yml` als kanonisch sichtbar | ✅ | `agent-policy.yaml:16`, `AGENTS.md:27` |
| 5 | Verdict-Enum-Reihenfolge angleichen | ✅ | `schemas/run-evidence-pack.v1.schema.json:56-64` |
| 6 | `review_date`-Feld in Freeze dokumentiert | ✅ | `.vibe/promotion-readiness-freeze.yml:10-13` |
| 7 | Phase-C-Checkboxen sync (Export-Herkunft, Konflikt-Gate) | ✅ | `docs/foundations/repo-plan.md:79-80` (beide `[x]`) |
| 8 | `plan-execution-checklist.md` in `index.md` verlinkt | ✅ | `docs/index.md:27, 168` |
| 9 | Test für `validate_relations.py` | ✅ | `scripts/docmeta/test_validate_relations.py` vorhanden |

**Welle 1 ist vollständig umgesetzt** (9/9).

## Noch offene Punkte aus dem 2026-05-05-Audit

### P0 (bewusst verschoben in Welle 1)

| Punkt | Status | Notiz |
|-------|--------|-------|
| `validate_schema.py` globaler `errors = []` State | offen | `scripts/docmeta/validate_schema.py:66`. Verschoben weil großer Eingriff; viele Funktionen teilen den State. |
| Gemeinsamer `scripts/docmeta/_validators.py` (Loader/Validator-Bau in 7 Skripten dupliziert) | offen | P3 Refactor; höheres Regressionsrisiko. |
| `contracts/system_decision.schema.json` ohne `schema_version` | offen | `additionalProperties: false` + bestehende Decisions → Migrationsschritt nötig (bestehende Decisions zuerst um Feld erweitern, dann Schema erlauben). |

### P2 (Inhalts-Lücken)

| Punkt | Status nach Second Pass |
|-------|------------------------|
| `docs/onboarding/` leer (.gitkeep only) | mit Stub-README markiert (2026-05-18) |
| `docs/rules/`, `docs/syntheses/`, `docs/experiments/` leer | mit Stub-READMEs markiert (2026-05-18) |
| `decisions/{benchmark,export,policy}/` leer | mit Stub-READMEs markiert (2026-05-18); typisierte Namespaces dokumentiert |
| `catalog/technologies/` leer | bewusst unbefüllt (Repo-Plan-Anmerkung); kein Stub nötig |
| Expected-Orphan-Allowlist für Orphan-Generator | weiter offen; Architektur-Entscheidung |
| 113+ Orphan-Dokumente | viele by-design (exports, CONTEXT/INITIAL), unverändert |

### Aus dem Repo-Plan / Roadmap erkennbar offen

- **Phase C — Staleness:** Bewusst dormant gehalten durch
  `decisions/system/2026-04-23-catalog-staleness-dormant.yml`. Generator
  `generate_stale_entries.py` darf nicht ohne semantischen Entscheid gebaut werden.
- **Phase C — Weak-Links / Diagnose-Kopplung:** `generate_weak_links.py` fehlt.
  Hängt an Staleness-Signal, also indirekt blockiert.
- **Phase C — Benchmark-Challenge-Versionierung:** `challenge_version` in
  `decision.yml` nicht erzwungen.
- **Phase C — Erweiterte Governance:** GitHub-Rulesets fürs Zonenmodell offen.
- **Phase D — gesamter Block:** Playbooks/Onboarding-Tiefenausbau, breitere
  Tool-Abdeckung, `generate_knowledge_gaps.py` / `generate_supersession_map.py`,
  Reaktiver Loop, Archivierungsstrategie, MCP-Bot — bewusst nicht in Arbeit.

### Aus der Roadmap (RM-001 bis RM-007)

- **RM-001** Agent-Operability Phase E Fixture-Erweiterung — laufend (P2)
- **RM-002** Evidence-Control-Plane — PR 10/11 abgeschlossen, Outcome-Evidence
  pilotiert, vollständige Auditor-Unabhängigkeit offen (P1)
- **RM-003** RRG-v0.2 Remediation — drei Drift-Klassen, Strategie-Entscheid offen (P2)
- **RM-004** Blueprint v2 Phase 2 Falsifizierbarkeitsschutz — Phase 1 läuft (P3)
- **RM-005** Agent/Skill Minimal Layer Usefulness-Evaluation — blockiert (P1)
- **RM-006** Catalog Staleness — dormant (P3)
- **RM-007** Plan-Execution-Checklist Phase 3/4 — kleine Restarbeiten (P2)

Diese Stränge sind alle bewusst menschlich gesteuert; keine Auto-Bewegung sinnvoll.

## Second-Pass-Fixes (in dieser Session umgesetzt)

| # | Datei / Pfad | Risiko | Effekt |
|---|---|---|---|
| 1 | `docs/foundations/repo-plan.md` Frontmatter `updated:` | trivial | Datum von 2026-04-23 auf 2026-05-18, „Teilstand"-Absatz aktualisiert |
| 2 | `docs/onboarding/README.md` (neu) | trivial | Stub: erklärt Phase-D-Status, verweist auf README/CONTRIBUTING/AGENTS |
| 3 | `docs/rules/README.md` (neu) | trivial | Stub: nennt aktive Regelquellen (`AGENTS.md`, `.vibe/*`, `policies/`) |
| 4 | `docs/syntheses/README.md` (neu) | trivial | Stub: grenzt gegen `evaluations/`, `concepts/`, `catalog/` ab |
| 5 | `docs/experiments/README.md` (neu) | trivial | Stub: trennt Docs-Ebene vom operativen `/experiments/`-Labor |
| 6 | `decisions/benchmark/README.md` (neu) | trivial | Stub: Zweck des typisierten Namespaces, kein Pflicht-Contract |
| 7 | `decisions/export/README.md` (neu) | trivial | Stub: verweist auf aktive Export-Logik (`.vibe/generated-artifacts.yml`) |
| 8 | `decisions/policy/README.md` (neu) | trivial | Stub: verweist auf aktive Policies in `docs/policies/` |

**Wirkung:** Wer im Repo landet, sieht jetzt für jeden Stub-Namespace *warum*
er noch keine fachlichen Artefakte enthält und *womit* der intendierte Inhalt
aktuell abgedeckt wird. Keine Code-Änderung, kein neuer Generator.
Keine Berührung von `AGENTS.md`, `repo.meta.yaml` oder `agent-policy.yaml`;
`docs/foundations/repo-plan.md` wurde bewusst als `canonicality: foundational`
Kontext aktualisiert (Teilstand, updated-Datum).

## Bewusst NICHT umgesetzt (autonome Begrenzung)

- `validate_schema.py` globaler State: zu großer Eingriff für autonome Session
- `_validators.py`-Extraktion: 7 Skripte touchieren, Regressionsrisiko zu hoch
- `system_decision.schema.json` `schema_version`: braucht Decision-Updates zuerst
- Staleness-Generator: per Decision dormant, **darf nicht** ohne Semantik-Entscheid
- Phase-D-Implementierungen: Architektur-Themen, nicht autonom entscheidbar
- Editieren von `AGENTS.md`, `repo.meta.yaml`, `agent-policy.yaml`: explizit verboten
- Experiment-Status ändern: ohne belegte Grundlage verboten
- Generierte Artefakte (`docs/_generated/*`, `exports/*`): nie manuell

## Validation

```
make validate   # vorher: ✅ passed
make validate   # nachher: ✅ passed
```

## Post-Review-Rework (nach Copilot-/Codex-Review)

Nach Review-Iterationen ergänzt:

| # | Änderung | Begründung |
|---|----------|------------|
| R1 | `docs/index.md` Body-Links für vier Stub-Namespaces (Folder-Link → README.md-Link) | Frontmatter-Relations allein reichen nicht für menschliche Navigation |
| R2 | `decisions/README.md` als inbound Navigation Surface für `decisions/{benchmark,export,policy}/README.md` | Echte Orphan-Lösung statt generiertem Pflaster; Decision-Stubs aus Orphan-Liste raus |
| R3 | `docs/index.md` verlinkt `decisions/README.md` in Frontmatter und Body (neuer Abschnitt „Decisions") | Konsistenz: decisions/ war bisher in docs/index.md unsichtbar |
| R4 | `.vibe/artifact-taxonomy.yml`: zwei Regeln für `decisions/README.md` und `decisions/*/README.md` vor dem `decisions/**`-Catchall | Verhindert Fehlklassifikation als `decision_record`; Stubs sind Navigation Surfaces |

**Wirkung:** Der Artifact-Taxonomy-Generator klassifiziert `decisions/README.md`
und `decisions/*/README.md` jetzt korrekt als `navigation_index` / `navigation_surface`
statt als `decision_record`. Kein falsches Governance-Audit-Signal mehr.

**Nicht verändert:** Keine Berührung von `AGENTS.md`, `repo.meta.yaml`, `agent-policy.yaml`.
Alle `docs/_generated/*`-Dateien ausschließlich durch Generatoren geändert.
