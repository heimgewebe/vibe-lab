---
title: "Evidence-Control-Plane — Diagnose nach Merge PR #189"
status: draft
canonicality: diagnosis
created: "2026-05-16"
triggered_by: "user-request-2026-05-16-diag-post-pr189"
stop_criterion: "Dieser PR setzt ausschließlich Option A um; Option B/C bleiben separate Kandidaten. Weitere Patches in diesem Diagnose-Track erfordern neue Ziel-Dateien, Ziel-Claims und Validator-Gates."
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

> **Zweck dieser Datei:** Diagnose-Artefakt nach Merge PR #189; dieser PR setzt zusätzlich Option A / Check C-2 um.
> Konsolidierung offener Qualitätsgates und Metrikblocker aus den Quellen nach Stand run-007 bis run-010.

---

## 0. Status dieses PR

Dieser PR enthält zwei Teile:

1. Diagnose nach Merge PR #189.
2. Umsetzung von Option A / Check C-2:
   `REPO_LOCAL_EVIDENCE_PATH_NOT_FOUND` in
   `scripts/docmeta/validate_claim_evidence.py`.

Nicht enthalten:
- Option B / Timing-Artifact-Kopplung.
- Option C / PR-4-Fixture-Konsolidierung.
- CI-Global-Enforce für `review_evidence_artifact`.
- Neue Runs.

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
| P-03 | Timing-Semantik | run-009: `capture_mode`, `evidence_status: self_reported`, `upgrade_path`-Notiz in `timing.txt`; run-008 enthält `timing.txt` als Timing-Artefakt | Offen bleibt der Enforcement-Blocker: Ohne `timing_artifact`-Kopplung erzwingt der Validator kein technisch belegtes `repo_local`-Timing. |
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
`validate_run_bundle.py` umgesetzt. C-3 bleibt offener Kandidat.

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

### Option B — Mittelgroßer Patch: Check C-1 (Timing-Artifact-Kopplung)

**Ziel-Dateien:**
- `scripts/docmeta/validate_run_bundle.py` — neues `timing_artifact`-Gate in `_validate_run_dir()`,
  analoges Pattern zu `changed_files_artifact` / `review_evidence_artifact`
- `.vibe/timing-artifact.contract.md` — neues Contract-Dokument (analog `.vibe/review-rework-artifact.contract.md`)

**Ziel-Claims:** `measurement.yml`-Feld `task_completion_time_observed.evidence_status: repo_local`

**Validator-Gate:** Wenn `evidence_status == "repo_local"` → `comparability.yml.timing_artifact`
muss gesetzt sein und auf existierende run-lokale Datei zeigen.

**Risiko (mittel):** Erfordert neues Contract-Dokument. Alle zukünftigen Runs mit
`task_completion_time_observed: repo_local` müssen ein `timing_artifact` in
`comparability.yml` setzen. Bestehende Runs (run-007 bis run-010) haben
`self_reported` — kein Breaking Change. Größerer Diff als Option A.

**Nutzen (hoch):** Schließt die letzte nicht-gegated Metrik. Nach diesem Patch
sind alle drei zentralen Outcome-Metriken (`scope_drift_count`, `review_friction_count` /
`rework_count`, `task_completion_time_observed`) an konkrete Artefakt-Existenz gekoppelt,
wenn `repo_local` behauptet wird.

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

## 5. Status nach diesem PR

**Umgesetzt in diesem PR:**
- Option A / Check C-2: `REPO_LOCAL_EVIDENCE_PATH_NOT_FOUND` in `validate_claim_evidence.py`.

**Weiterhin offen — erfordert Sichtung vor Patch-Start:**
- Tatsächlicher Zustand von `tests/fixtures/claim_evidence/` (Option C) — Dateisystem
  nicht ausgelesen.
- Tatsächlicher Zustand der `evidence-pack.yml`-Dateien in run-007 bis run-010 bzgl.
  `self_reported`-Evidence (für Check C-3) — YAML-Inhalt nicht ausgelesen.
- Entscheidung, ob CI-Global-Enforce für `review_evidence_artifact` (§2.3) als
  eigener PR gewertet wird oder als Teil von Option B/C.

**Kein weiterer Patch vor Entscheidung über:**
- Option B (Timing-Artifact-Kopplung).
- Option C (PR-4-Fixture-Konsolidierung).
- CI-Global-Enforce für `review_evidence_artifact`.
