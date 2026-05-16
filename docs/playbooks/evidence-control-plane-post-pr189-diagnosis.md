---
title: "Evidence-Control-Plane — Diagnose nach Merge PR #189"
status: draft
canonicality: diagnosis
created: "2026-05-16"
triggered_by: "user-request-2026-05-16-diag-post-pr189"
stop_criterion: "Option B umgesetzt; kein weiterer Patch ohne neue Ziel-Dateien, Ziel-Claims und Validator-Gates."
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
---

# Evidence-Control-Plane — Diagnose nach Merge PR #189

> **Zweck dieser Datei:** Diagnose-Artefakt nach Merge PR #189, plus Umsetzung von Option A (Check C-2) und Option B (Check C-1) in aufeinanderfolgenden PRs.
> Konsolidierung offener Qualitätsgates und Metrikblocker aus den Quellen nach Stand run-007 bis run-010.

---

## 0. Status dieses PR

Dieser PR enthält zwei Teile:

1. Diagnose nach Merge PR #189.
2. Umsetzung von Option A / Check C-2:
   `REPO_LOCAL_EVIDENCE_PATH_NOT_FOUND` in
   `scripts/docmeta/validate_claim_evidence.py`.

Nicht enthalten (PR des Diagnose-Dokuments):
- Option B / Timing-Artifact-Kopplung.
- Option C / PR-4-Fixture-Konsolidierung.
- CI-Global-Enforce für `review_evidence_artifact`.
- Neue Runs.

---

## 0b. Status Folge-PR (Option B)

Dieser Abschnitt dokumentiert den Folge-PR, der Option B implementiert.

Umgesetzt:
- Option B / Check C-1: `timing_artifact`-Gate in `validate_run_bundle.py`.
- Migration run-008: `timing_artifact: "timing.txt"` in `comparability.yml` gesetzt.

Nicht enthalten:
- Option C / PR-4-Fixture-Konsolidierung.
- CI-Global-Enforce für `review_evidence_artifact`.
- Neue Runs.
- Umsetzung von Option C / PR-4-Fixture-Konsolidierung.

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
| P-02 | Negativfall / CLAIM_NOT_PROVEN | run-008: `CLAIM_NOT_PROVEN` bei partieller Unabhängigkeit dokumentiert, `timing.txt` repo-lokal archiviert und an `timing_artifact` gekoppelt (Folge-PR) | Echter FAIL (Auditor blockiert Artefakt wegen Fehler) noch nicht belegt. |
| P-03 | Timing-Semantik | run-009: `capture_mode`, `evidence_status: self_reported`, `upgrade_path`-Notiz in timing.txt | Timing für run-009 und run-010 bleibt `self_reported`. run-008 ist `repo_local` mit `timing.txt`-Kopplung (Folge-PR). |
| P-04 | Externer Audit | run-010: different-session Audit mit `overall_verdict: PASS` für pack-001 bis pack-007 | `auditor_independence_status: PARTIAL`; gleiche Modellfamilie. Vollständige Unabhängigkeit nicht belegt. |
| P-05 | Audit-Request-Artefakt | run-010: `audit-request.md` spezifiziert exakt Scope, Claims und Output-Pfad für externen Auditor | Der externe Auditor hat (im different-session run) nur das Package validiert, nicht den Primärprozess. Blocker formal offen. |

### 1.3 In diesem PR erledigt

| # | Blocker | Umsetzung | Rest |
|---|---------|-----------|------|
| B-02 | PR-5: No PASS without existing/archived evidence file | `REPO_LOCAL_EVIDENCE_PATH_NOT_FOUND` in `validate_claim_evidence.py`; Negativ-Fixtures `repo-local-nonexistent-path.yml` (semantisch) und `repo-local-path-escape.yml` (schema-level); Checklist-Item auf `[x]` gesetzt | Validierung muss grün sein |
| B-02b | Timing-`repo_local` ohne Artefakt-Gate (Folge-PR) | `timing_artifact`-Gate in `validate_run_bundle.py`; Migration run-008: `timing_artifact: "timing.txt"` in `comparability.yml`; 8 Regressionstests in `test_validate_run_bundle.py` | Validierung muss grün sein |

---

## 2. Metriken mit Bedarf an Schema/Contract/Validator-Änderung

### 2.1 `task_completion_time_observed` — Gate implementiert (Folge-PR)

**Status:** Umgesetzt in Folge-PR (Option B / Check C-1).

`validate_run_bundle.py` prüft nun: wenn
`metrics.task_completion_time_observed.evidence_status == "repo_local"` →
`comparability.yml` muss ein Feld `timing_artifact` enthalten, das auf eine
existierende, run-lokale Datei zeigt.

- run-008: `evidence_status: repo_local`, `timing_artifact: "timing.txt"` gesetzt ✓
- run-009: `evidence_status: self_reported` — kein Gate feuert ✓
- run-010: `evidence_status: self_reported` — kein Gate feuert ✓
- run-005/006: Timing nicht als `repo_local` deklariert — kein Gate feuert ✓

**Analoger Mechanismus** existiert für `scope_drift_count`
(→ `changed_files_artifact`) und `review_friction_count` / `rework_count`
(→ `review_evidence_artifact`). Alle drei zentralen Outcome-Metriken sind
nun an konkrete Artefakt-Existenz gekoppelt, wenn `repo_local` behauptet wird.

### 2.2 `validate_claim_evidence.py` — Datei-Existenz-Prüfung für `repo_local`

**Status:** In diesem PR umgesetzt.

`validate_claim_evidence.py` prüft nun für Evidence-Einträge mit
`status: repo_local`, ob `evidence.path` unter `REPO_ROOT` auf eine existierende
Datei zeigt. Fehlende Dateien erzeugen `REPO_LOCAL_EVIDENCE_PATH_NOT_FOUND`.

Path-Escape-Versuche (z. B. `../../outside.txt`) werden bereits durch das JSON-Schema
geblockt (`evidence.path`-Pattern schlägt fehl → Exit 2, vor semantischen Prüfungen).
`REPO_LOCAL_EVIDENCE_PATH_OUTSIDE_REPO` in `repo_local_existence_errors()` ist daher
Defense-in-depth und im normalen CLI-Pfad nicht erreichbar.

Analoger Mechanismus existiert bereits in `validate_run_bundle.py` (`_resolve_within()`
+ expliziter Fehler "verlässt das Repo"). Beide Validatoren sind nun konsistent.

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

C-2 ist im Diagnose-PR umgesetzt; C-1 ist im Folge-PR umgesetzt; C-3 bleibt offener Kandidat.

### Check C-1 — Timing-Artifact-Kopplung — **umgesetzt in Folge-PR**

**Status:** Umgesetzt.

Implementierung: `validate_run_bundle.py`, Funktion `_validate_run_dir()`.
Analoges Pattern zu `changed_files_artifact` / `review_evidence_artifact`.
Genutzt: generischer Resolver `_load_comparability_run_artifact_ref()`.

Geänderte Dateien:
- `scripts/docmeta/validate_run_bundle.py` — `timing_artifact`-Gate + `timing_artifact_valid` in `_validate_run_dir()`
- `scripts/docmeta/test_validate_run_bundle.py` — 8 Regressionstests in `TimingArtifactTests`
- `experiments/.../run-008-.../comparability.yml` — `timing_artifact: "timing.txt"` ergänzt
- `docs/playbooks/evidence-control-plane-post-pr189-diagnosis.md` — dieser Abschnitt aktualisiert

Timing-Status der Runs:
- run-008: `repo_local`, `timing_artifact: "timing.txt"` ✓
- run-009: `self_reported` mit `timing.txt` (kein Gate feuert)
- run-010: `self_reported` mit `ci-or-git-timing.txt` (kein Gate feuert)
- run-005/run-006: Timing `missing_evidence` (kein Gate feuert)

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

### Check C-3 — `self_reported`-Timing darf kein PASS-Claim-Beleg sein

**Was:** `validate_claim_evidence.py` oder `validate_run_bundle.py`:
wenn ein `evidence-pack.yml`-Claim `verdict: PASS` hat und alle Evidence-Einträge
`status: self_reported` (oder kein Status) haben → Block mit Rule-ID
`PASS_WITH_SELF_REPORTED_ONLY`.

**Ziel-Datei:** `scripts/docmeta/validate_claim_evidence.py`,
Funktion `semantic_errors_for_claim()`

**Ziel-Claims:** Jeder `verdict: PASS`-Claim in `evidence-pack.yml` mit
ausschließlich `self_reported` Evidence.

**Warum minimal:** `self_reported` ist derzeit kein `STRONG_EVIDENCE_STATUS`
in `validate_claim_evidence.py` (Zeile 27–32), aber auch kein explizit verbotenes
Evidence für PASS. Der Status `external_unverified` ist bereits geblockt
(`PASS_WITH_EXTERNAL_UNVERIFIED_ONLY`, Zeile 221–229). `self_reported` fehlt
in dieser Abgrenzung.

**Risiko:** `self_reported` in `evidence-pack.yml` ist aktuell selten —
die meisten Timing-Daten sind in `measurement.yml` (nicht in `evidence-pack.yml`).
Wenn kein Run ein `evidence-pack.yml`-Claim mit `self_reported` und `PASS` hat,
wäre das ein No-Op-Gate. Muss gegen tatsächliche `evidence-pack.yml`-Dateien
geprüft werden, bevor implementiert wird.

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

### Option B — **umgesetzt in Folge-PR**: Check C-1 (Timing-Artifact-Kopplung)

**Status:** Umgesetzt.

Geänderte Dateien:
- `scripts/docmeta/validate_run_bundle.py` — `timing_artifact`-Gate in `_validate_run_dir()`
- `scripts/docmeta/test_validate_run_bundle.py` — `TimingArtifactTests` mit 8 Regressionstests
- `experiments/.../run-008-.../comparability.yml` — `timing_artifact: "timing.txt"` ergänzt
- `docs/playbooks/evidence-control-plane-post-pr189-diagnosis.md` — Diagnose aktualisiert

Kein neues Contract-Dokument angelegt: Validator-Text in Diagnose und Tests ist ausreichend.
Bestehende Runs (run-007 bis run-010 außer run-008) nutzen `self_reported` — kein Breaking Change.

---

### Option C — Konsolidierungs-Patch: PR-4-Checkliste schließen + Fixtures vervollständigen

**Ziel-Dateien:**
- `schemas/run-evidence-pack.v1.schema.json` — prüfen ob vollständig (invalid-Fälle
  abgedeckt?)
- `tests/fixtures/claim_evidence/` — prüfen ob Verzeichnis und Fixtures existieren;
  fehlende anlegen
- `scripts/docmeta/test_validate_claim_evidence.py` — Negativ-Fixtures für:
  - `invalid status`
  - `fehlende run_id`
  - `path escape` (`../../secrets.txt`)
  - `leere Pfade`
- Checklist §PR 4 — alle vier Items abhaken

**Ziel-Claims:** Formale PR-4-Checkliste (`[ ]` → `[x]`)

**Validator-Gate:** Keine neuen Gates. Bestehende Gates durch Tests abgedeckt.

**Risiko (niedrig bis mittel):** Erfordert Sichtung der tatsächlichen Fixture-Lage
(bekannt: Validator läuft und ist grün — unklar ob Fixtures für alle Negativ-Fälle
existieren). Möglicher Befund: PR-4-Items sind de facto erledigt, nur nie abgehakt.

**Nutzen (gering bis mittel):** Dokumentarische Bereinigung. Verhindert keine
neuen Fehler. Wichtig für Klarheit über tatsächlichen Reifegrad des Validators.

---

## 5. Status nach beiden PRs

**Umgesetzt:**
- Option A / Check C-2: `REPO_LOCAL_EVIDENCE_PATH_NOT_FOUND` in `validate_claim_evidence.py`.
- Option B / Check C-1: `timing_artifact`-Gate in `validate_run_bundle.py`; run-008 migriert.

**Weiterhin offen — erfordert Sichtung vor Patch-Start:**
- Tatsächlicher Zustand von `tests/fixtures/claim_evidence/` (Option C) — Dateisystem
  nicht ausgelesen.
- Tatsächlicher Zustand der `evidence-pack.yml`-Dateien in run-007 bis run-010 bzgl.
  `self_reported`-Evidence (für Check C-3) — YAML-Inhalt nicht ausgelesen.
- Entscheidung, ob CI-Global-Enforce für `review_evidence_artifact` (§2.3) als
  eigener PR gewertet wird oder als Teil von Option C.

**Kein weiterer Patch vor Entscheidung über:**
- Option C (PR-4-Fixture-Konsolidierung).
- CI-Global-Enforce für `review_evidence_artifact`.
- Check C-3 (`self_reported`-Timing als PASS-Beleg).
