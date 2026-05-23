---
title: "Evidence-Control-Plane — Diagnose nach Merge PR #189"
status: draft
canonicality: diagnosis
created: "2026-05-16"
triggered_by: "user-request-2026-05-16-diag-post-pr189"
stop_criterion: "Der Reconciliation-Track dokumentiert C-1/C-2 als umgesetzt, klärt C-3 als durch PASS_WITHOUT_STRONG_EVIDENCE abgedeckt und schließt PR-4 dokumentarisch auf Basis bestehender Fixtures/Gates. Weitere Patches in diesem Diagnose-Track reagieren nur auf neue Belege oder neue Drift-Signale."
relations:
  - type: references
    target: evidence-control-plane-roadmap-checklist.md
  - type: references
    target: ../roadmap.md
  - type: references
    target: ../blueprints/blueprint-evidence-control-plane-v1.md
  - type: references
    target: ../../experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/results/decision.yml
  - type: references
    target: ../../experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/results/cross-run-assessment.md
  - type: references
    target: ../../.vibe/review-rework-artifact.contract.md
  - type: references
    target: ../../schemas/review-events.v1.schema.json
  - type: references
    target: ../../scripts/docmeta/validate_claim_evidence.py
  - type: references
    target: ../../scripts/docmeta/validate_run_bundle.py
  - type: references
    target: ../../experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/artifacts/run-011-external-outcome-audit-prep/audit-request.md
---

# Evidence-Control-Plane — Diagnose nach Merge PR #189

> **Zweck dieser Datei:** Diagnose-Artefakt nach Merge PR #189; der aktuelle Stand setzt Option A/B (Check C-2 + C-1) um.
> Konsolidierung offener Qualitätsgates und Metrikblocker aus den Quellen nach Stand run-007 bis run-010.

---

## 0. Status dieses Tracks

Der aktuelle Stand enthält:

1. Diagnose nach Merge PR #189.
2. Umsetzung von Option A / Check C-2:
   - `REPO_LOCAL_EVIDENCE_PATH_NOT_FOUND` in `scripts/docmeta/validate_claim_evidence.py`.
3. Umsetzung von Option B / Check C-1:
   - `timing_artifact`-Kopplung fuer `task_completion_time_observed.evidence_status=repo_local` in `scripts/docmeta/validate_run_bundle.py`.

Nicht enthalten:
- CI-Global-Enforce für `review_evidence_artifact`.
- Neue Runs.

Ergaenzung (2026-05-20, Run-011-Reconciliation):
- Neuer vorbereiteter Track angelegt:
  `artifacts/run-011-external-outcome-audit-prep/`.
- Zweck: externe Outcome-Pruefung fuer RM-002/RM-005 vorbereiten.
- Epistemische Leerstelle explizit: externer unabhaengiger Auditor-Output fehlt.
- Kein Upgrade von `insufficient_proof` oder gleichwertiger Nicht-PASS-Lage ohne
  externen Input.

---

## 1. Offene Blocker — Real vs. Teilweise erledigt

### 1.1 Echte, ungelöste Blocker

| # | Blocker | Quelle | Warum noch real |
|---|---------|--------|-----------------|
| B-01 | **PR-4-Checklist nie abgehakt**: `schemas/run-evidence-pack.v1.schema.json`, Fixtures in `tests/fixtures/claim_evidence/*`, Schema-Validierung inkl. invalid-Fälle | Checklist §PR 4: alle vier Items `[ ]` | Der Validator (PR 5) existiert und lädt das Schema zur Laufzeit — aber die PR-4-Checkliste ist nie als erledigt markiert worden. Unklar, ob Fixtures und Negativ-Fixture-Tests vollständig grün sind. |
| B-03 | **Alle Durchgehenden Qualitätsgates unbelegt** | Checklist §Durchgehende Qualitätsgates: alle `[ ]` | Keine einzige der fünf Metriken (`claim_to_evidence_binding_rate`, `unsupported_claim_count`, `validation_gap_count`, `contradiction_count`, `external_unverified_ratio`) hat einen Validator-Gate, der ihren Trend über PRs hinweg misst oder blockiert. Sie sind nur im Blueprint benannt. |
| B-04 | **Definition of Done komplett offen** | Checklist §Definition of Done: alle `[ ]` | Die drei DoD-Punkte (verbindliche Verankerung, PASS-Blocking, technische Absicherung von Self-Observation/Artefaktgrenzen) sind formal nicht erfüllt, obwohl Validator-Code existiert. |
| B-05 | **Vollständig unabhängiger Auditor fehlt** | `decision.yml` next_steps §4; `cross-run-assessment.md` §5; `roadmap.md` RM-005 Blocker | run-010 hat `auditor_independence_status: PARTIAL` (gleiche Modellfamilie). Ein Auditor eines anderen AI-Systems oder ein Human-Reviewer ist noch nicht belegt. Experiment-Verdict bleibt `insufficient_proof`. |
| B-06 | **Task-Diversität nicht repliziert** | `cross-run-assessment.md` §5; `decision.yml` next_steps §2 | run-009 claim-002 PASS (task außerhalb validator-test-hardening-Cluster) ist ein Einzelbeleg. Kein zweiter unabhängiger Run in einer weiteren Task-Klasse vorhanden. |
| B-07 | **Echter Negativfall (FAIL-Verdict) fehlt** | `cross-run-assessment.md` §5 | run-008 pilotiert `CLAIM_NOT_PROVEN` (nicht echtes FAIL). Kein Run dokumentiert, wo der Auditor einen tatsächlichen Fehler identifiziert und blockiert hat. |

### 1.2 Durch run-007 bis run-010 teilweise erledigte Blocker

| # | Blocker | Was erledigt | Was bleibt offen |
|---|---------|--------------|-----------------|
| P-01 | review_friction_count / rework_count persistent null | run-007: Schema-backed contract (`.vibe/review-rework-artifact.contract.md` v0.2) + `schemas/review-events.v1.schema.json` + Validator-Kopplung in `validate_run_bundle.py` aktiv; run-007 hat **echte** `review-events.yml` mit `repo_local` Daten | Kein zweiter Run mit echten Review-Events. Einmalige Pilotierung, keine Replikation. |
| P-02 | Negativfall / CLAIM_NOT_PROVEN | run-008: `CLAIM_NOT_PROVEN` bei partieller Unabhängigkeit dokumentiert, `timing.txt` repo-lokal archiviert | Echter FAIL (Auditor blockiert Artefakt wegen Fehler) noch nicht belegt. |
| P-03 | Timing-Semantik | run-009: `capture_mode`, `evidence_status: self_reported`, `upgrade_path`-Notiz in `timing.txt`; run-008 enthält `timing.txt` als Timing-Artefakt | Die `repo_local`-Kopplung ist durch `timing_artifact` umgesetzt. Offen bleibt nur die methodische Vergleichbarkeit von `self_reported` Timing-Werten (kein neuer Validator-Blocker in diesem Track). |
| P-04 | Externer Audit | run-010: different-session Audit mit `overall_verdict: PASS` für pack-001 bis pack-007 | `auditor_independence_status: PARTIAL`; gleiche Modellfamilie. Vollständige Unabhängigkeit nicht belegt. |
| P-05 | Audit-Request-Artefakt | run-010: `audit-request.md` spezifiziert exakt Scope, Claims und Output-Pfad für externen Auditor | Der externe Auditor hat (im different-session run) nur das Package validiert, nicht den Primärprozess. Blocker formal offen. |

### 1.3 In diesem PR erledigt

| # | Blocker | Umsetzung | Rest |
|---|---------|-----------|------|
| B-02 | PR-5: No PASS without existing/archived evidence file | `REPO_LOCAL_EVIDENCE_PATH_NOT_FOUND` in `validate_claim_evidence.py`; Negativ-Fixtures `repo-local-nonexistent-path.yml` (semantisch) und `repo-local-path-escape.yml` (schema-level); Checklist-Item auf `[x]` gesetzt | Validierung muss grün sein |

---

## 2. Metriken mit Bedarf an Schema/Contract/Validator-Änderung

### 2.1 `task_completion_time_observed` — kein Gate existiert

**Problem:** `measurement.yml` kann `task_completion_time_observed.evidence_status: repo_local`
deklarieren, ohne dass `validate_run_bundle.py` prüft, ob eine Timing-Datei
(z. B. `timing.txt`) tatsächlich im Run-Verzeichnis existiert.

- **Analoger Mechanismus existiert bereits** für `scope_drift_count` (erfordert
  `changed_files_artifact` in `comparability.yml`) und für
  `review_friction_count` / `rework_count` (erfordert `review_evidence_artifact`).
- **Noch nicht existiert:** ein Contract für `task_completion_time_observed`, der
  `evidence_status: repo_local` an eine nachvollziehbare Datei koppelt.
- **Aktuelle Konsequenz:** Ein Run könnte `task_completion_time_observed: repo_local`
  behaupten, ohne dass eine Timing-Datei vorliegt. `validate_run_bundle.py` würde
  das nicht blockieren.

**Benötigte Änderung:**
- Ziel-Datei: `scripts/docmeta/validate_run_bundle.py`
- Ziel-Feld: `metrics.task_completion_time_observed.evidence_status`
- Gate: wenn `evidence_status == "repo_local"` → Pflicht-Feld
  `timing_artifact` in `comparability.yml` (analog `changed_files_artifact`),
  das auf eine existierende, run-lokale Datei zeigt.
- Schema-Änderung nötig? Nein (Validierung in Python, kein Schema-Enforcement nötig).
  Optional: `comparability.yml` um `timing_artifact`-Feld erweitern (kein Schema
  für comparability.yml vorhanden — das wäre ein neues Contract-Dokument).

### 2.2 `validate_claim_evidence.py` — Datei-Existenz-Prüfung für `repo_local`

**Status:** In diesem PR umgesetzt.

`validate_claim_evidence.py` prüft nun für Evidence-Einträge mit
`status: repo_local`, ob `evidence.path` unter `REPO_ROOT` auf eine existierende
Datei zeigt. Fehlende Dateien erzeugen `REPO_LOCAL_EVIDENCE_PATH_NOT_FOUND`.

Path-Escape-Versuche (z. B. `../../outside.txt`) werden bereits durch das JSON-Schema
geblockt (`evidence.path`-Pattern schlägt fehl → Exit 2, vor semantischen Prüfungen).
`REPO_LOCAL_EVIDENCE_PATH_OUTSIDE_REPO` in `repo_local_existence_errors()` ist daher
Defense-in-depth und im normalen CLI-Pfad nicht erreichbar.

Die frühere Inline-Prüfung in `validate_run_bundle.py` ist nicht mehr die primäre
Autorität; `repo_local`-Existenz wird über `validate_claim_evidence_file()`
validiert.

### 2.3 `review_friction_count` / `rework_count` — Contract aktiv, aber CI-Enforcement fehlt

**Problem:** Das Contract (`.vibe/review-rework-artifact.contract.md` v0.2) ist
`schema-backed` und der Validator (`validate_run_bundle.py`) prüft
`review_evidence_artifact` wenn vorhanden. Aber:

- **Kein globales CI-Enforce** für neue Runs: neue Runs können `review_friction_count:
  null / missing_evidence` ohne `review_evidence_artifact` einreichen — das wird
  nicht blockiert, nur toleriert.
- **Contract sagt explizit** (`§Operationalization Status`):
  `CI global: Future — Planned: CI hard-fail for all new runs without review-events.yml (not this PR)`

**Was fehlt:** Ein CI-Gate-Upgrade von "optional wenn vorhanden" auf "Pflicht
für neue Runs". Das erfordert eine Policy-Entscheidung (CI schlägt fehl für alle
neuen Runs ohne review-events.yml), nicht nur eine Validator-Erweiterung.

---

## 3. Minimale Checks gegen falsche Belegung von Timing/Review/Rework

C-2 ist umgesetzt. C-1 ist durch das `timing_artifact`-Gate in
`validate_run_bundle.py` umgesetzt. Der C-3-Fall ist bereits durch die
generische Strong-Evidence-Regel (`PASS_WITHOUT_STRONG_EVIDENCE`) abgedeckt.

### Check C-1 — Timing-Artifact-Kopplung — umgesetzt

**Was:** `validate_run_bundle.py` prüft: wenn
`metrics.task_completion_time_observed.evidence_status == "repo_local"` →
`comparability.yml` muss ein Feld `timing_artifact` enthalten, das auf eine
existierende, run-lokale Datei zeigt.

**Ziel-Datei:** `scripts/docmeta/validate_run_bundle.py`, Funktion `_validate_run_dir()`
(ca. Zeile 1359ff., wo bereits der analoge Check für `review_friction_count` steht)

**Ziel-Claim:** Jeder `measurement.yml`-Eintrag mit
`task_completion_time_observed.evidence_status: repo_local`

**Warum minimal:** Analoger Mechanismus existiert für `scope_drift_count`
(→ `changed_files_artifact`) und `review_friction_count` / `rework_count`
(→ `review_evidence_artifact`). Pattern ist etabliert, kein neues Schema nötig.

**Risiko:** run-008/009/010 haben `timing.txt` / `ci-or-git-timing.txt` als
`self_reported` deklariert — diese würden durch diesen Check nicht blockiert
(nur `repo_local` wird gegated). Kein breaking change für bestehende Runs.

### Check C-2 — Evidence-Datei-Existenz in validate_claim_evidence.py (B-02) — umgesetzt in diesem PR

**Status:** Umgesetzt.

Implementierung: `validate_claim_evidence.py`, neue Funktion `repo_local_existence_errors()`
aufgerufen aus `semantic_errors_for_claim()`. Für `evidence.status == "repo_local"` →
prüft ob `REPO_ROOT / evidence.path` existiert. Rule-ID: `REPO_LOCAL_EVIDENCE_PATH_NOT_FOUND`
für fehlende repo-lokale Dateien. `REPO_LOCAL_EVIDENCE_PATH_OUTSIDE_REPO` ist Defense-in-depth
für direkten programmatischen Aufruf; im normalen CLI-Pfad blockt das JSON-Schema
path escapes (z. B. `../../outside.txt`) bereits mit Exit 2 vor der semantischen Prüfung.

Geänderte Dateien:
- `scripts/docmeta/validate_claim_evidence.py`
- `scripts/docmeta/test_validate_claim_evidence.py`
- `tests/fixtures/claim_evidence_semantic/invalid/repo-local-nonexistent-path.yml`
- `tests/fixtures/claim_evidence_semantic/invalid/repo-local-path-escape.yml`
- `tests/fixtures/claim_evidence_semantic/valid/pass-with-repo-local-test-output.yml`
- `tests/fixtures/claim_evidence_semantic/valid/test-output.txt`

### Check C-3 — `self_reported`-only PASS-Claims

**Status:** Kein separater Spezial-Validator erforderlich.

`validate_claim_evidence.py` blockiert PASS-Claims ohne starken Evidence-Status
bereits über `PASS_WITHOUT_STRONG_EVIDENCE`. Der Fall ist explizit über
`tests/fixtures/claim_evidence_semantic/invalid/pass-with-self-reported-only.yml`
abgedeckt. Damit ist die gewünschte Schutzwirkung vorhanden, ohne zusätzliche
Rule-ID-Dopplung.

Belegt durch:
- `tests/fixtures/claim_evidence_semantic/invalid/pass-with-self-reported-only.yml` — Negativ-Fixture, erkannt als Violation.
- Testlauf: `make validate-claim-evidence-tests` (Bestandteil von `make validate`).
- `make validate` → EXIT_CODE=0 (2026-05-20).

---

## 4. Patch-Optionen (maximal 3, mit Risiko/Nutzen)

### Option A — umgesetzt in diesem PR: Check C-2

**Status:** Umgesetzt.

Geänderte Dateien:
- `scripts/docmeta/validate_claim_evidence.py` — neue Funktion `repo_local_existence_errors()` in `semantic_errors_for_claim()`
- `scripts/docmeta/test_validate_claim_evidence.py` — Negativ-Fixture-Test für `REPO_LOCAL_EVIDENCE_PATH_NOT_FOUND`; separater Schema-Test für path escape (`../../outside.txt`, Exit 2)
- `tests/fixtures/claim_evidence_semantic/invalid/repo-local-nonexistent-path.yml` — Negativ-Fixture: semantischer Fehler, Exit 1
- `tests/fixtures/claim_evidence_semantic/invalid/repo-local-path-escape.yml` — Schema-Boundary-Proof: Exit 2 (`evidence.path`-Pattern rejects `../../...`)
- `tests/fixtures/claim_evidence_semantic/valid/pass-with-repo-local-test-output.yml` — Pfad auf existierende Datei korrigiert
- `tests/fixtures/claim_evidence_semantic/valid/test-output.txt` — neues Stub-Artefakt
- `docs/playbooks/evidence-control-plane-roadmap-checklist.md` — Checklist-Item `[x]` gesetzt

Rule `REPO_LOCAL_EVIDENCE_PATH_NOT_FOUND` blockiert PASS und non-PASS-Claims
gleichermaßen. Standalone-CLI (`validate-claim-evidence`) ist nun vollständig.

---

### Option B — umgesetzt: Check C-1 (Timing-Artifact-Kopplung)

**Status:** Umgesetzt in `scripts/docmeta/validate_run_bundle.py`.

**Ziel-Claims:** `measurement.yml`-Feld `task_completion_time_observed.evidence_status: repo_local`

**Validator-Gate:** Wenn `evidence_status == "repo_local"` → `comparability.yml.timing_artifact`
muss gesetzt sein und auf existierende run-lokale Datei zeigen.

**Risiko:** Bestehende Runs mit `self_reported` bleiben unverändert; nur
`repo_local` wird an ein vorhandenes Timing-Artefakt gekoppelt.

**Nutzen (hoch):** Schließt die letzte nicht-gegated Metrik. Nach diesem Patch
sind alle drei zentralen Outcome-Metriken (`scope_drift_count`, `review_friction_count` /
`rework_count`, `task_completion_time_observed`) an konkrete Artefakt-Existenz gekoppelt,
wenn `repo_local` behauptet wird.

---

### Option C — Reconciliation: PR-4-Checkliste mit belegtem Ist-Zustand schließen

**Status:** Dokumentarisch geschlossen im Reconciliation-Track.

Beleglage im aktuellen Stand:
- `schemas/run-evidence-pack.v1.schema.json` vorhanden.
- `tests/fixtures/claim_evidence/invalid/` enthält `missing-run-id`, `path-escape`,
  `empty-evidence-path`, `unknown-evidence-status`, `bad-schema-version`.
- `make validate-run-evidence-pack-schema-tests` muss grün sein
  (`scripts/docmeta/test_run_evidence_pack_schema.py`).
- PR-4 ist damit ueber Schema/Fixture-Coverage belegt; der semantische Claim-Evidence-Validator ist hier nicht der primaere Nachweis.

**Ziel-Claims:** Formale PR-4-Checkliste (`[ ]` → `[x]`)

**Validator-Gate:** Keine neuen Gates. Bestehende Gates werden über vorhandene Tests/Validierungsläufe belegt.
Bestehende Gates wurden über folgende Läufe belegt:
- `schemas/run-evidence-pack.v1.schema.json` vorhanden und schema-valide.
- `tests/fixtures/claim_evidence/invalid/` enthält `missing-run-id`, `path-escape`,
  `empty-evidence-path`, `unknown-evidence-status`, `bad-schema-version` — alle als invalid erkannt.
- `make validate-run-evidence-pack-schema-tests` → 2 tests OK (`scripts/docmeta/test_run_evidence_pack_schema.py`).
- `make validate` → EXIT_CODE=0.

**Risiko (niedrig):** Hauptfehler wäre ein vorzeitiges Abhaken ohne Testbeleg.

**Nutzen (gering bis mittel):** Dokumentarische Bereinigung. Verhindert keine
neuen Fehler. Wichtig für Klarheit über tatsächlichen Reifegrad des Validators.

---

## 5. Status im aktuellen Stand

**Umgesetzt im aktuellen Stand:**
- Option A / Check C-2: `REPO_LOCAL_EVIDENCE_PATH_NOT_FOUND` in `validate_claim_evidence.py`.
- Option B / Check C-1: `timing_artifact`-Kopplung in `validate_run_bundle.py`.
- C-3-Abdeckung über `PASS_WITHOUT_STRONG_EVIDENCE` statt Spezial-Rule.

**Weiterhin offen als separater Track:**
- CI-Global-Enforce für `review_evidence_artifact` (§2.3).
- Neue Runs für Auditor-Unabhängigkeit und Task-Diversität.
- Run-011 ist nur vorbereitet (`external_audit_requested`) und wartet auf
  externen Auditor-Output.

## Validation

Für diesen Reconciliation-Stand müssen folgende Checks grün sein:

Für diesen Reconciliation-Stand wurden folgende Checks ausgeführt und waren grün
(ausgeführt 2026-05-20; Beleg: `artifacts/run-011-external-outcome-audit-prep/make-validate.txt`):

| Check | Ergebnis |
|-------|----------|
| `make validate-run-evidence-pack-schema-tests` | ✅ 2 tests OK |
| `make validate-run-bundle-tests` | ✅ 147 tests OK |
| `make validate-run-bundle` | ✅ All run bundles consistent |
| `make validate-relations` | ✅ All relations valid (220 files) |
| `make validate` | ✅ Validation passed (EXIT_CODE=0) |
