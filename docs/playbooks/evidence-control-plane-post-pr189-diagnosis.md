---
title: "Evidence-Control-Plane — Diagnose nach Merge PR #189"
status: draft
canonicality: diagnosis
created: "2026-05-16"
triggered_by: "user-request-2026-05-16-diag-post-pr189"
stop_criterion: "Kein Patch, bevor exakte Ziel-Dateien, Ziel-Claims und Validator-Gates benannt sind."
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

> **Zweck dieser Datei:** Diagnose-Artefakt nach Merge PR #189, plus Umsetzung von Option A (Check C-2) im selben PR.
> Konsolidierung offener Qualitätsgates und Metrikblocker aus den Quellquellen nach Stand run-007 bis run-010.

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
| B-02 | ~~**PR-5 fehlt eine Regel**: `[ ] No PASS without existing/archived evidence file.`~~ **Erledigt in diesem PR.** | Checklist §PR 5: Item `[x]` | `REPO_LOCAL_EVIDENCE_PATH_NOT_FOUND` in `validate_claim_evidence.py` implementiert. Fixture `tests/fixtures/claim_evidence_semantic/invalid/repo-local-nonexistent-path.yml` belegt den Negativfall. |
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
| P-03 | Timing-Semantik | run-009: `capture_mode`, `evidence_status: self_reported`, `upgrade_path`-Notiz in timing.txt | Timing bleibt `self_reported`. Kein `repo_local` oder `external_verified` Timing-Beleg vorhanden. |
| P-04 | Externer Audit | run-010: different-session Audit mit `overall_verdict: PASS` für pack-001 bis pack-007 | `auditor_independence_status: PARTIAL`; gleiche Modellfamilie. Vollständige Unabhängigkeit nicht belegt. |
| P-05 | Audit-Request-Artefakt | run-010: `audit-request.md` spezifiziert exakt Scope, Claims und Output-Pfad für externen Auditor | Der externe Auditor hat (im different-session run) nur das Package validiert, nicht den Primärprozess. Blocker formal offen. |

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

### 2.2 `validate_claim_evidence.py` — fehlende Datei-Existenz-Prüfung (B-02)

**Problem:** `validate_claim_evidence.py` prüft `evidence.status` (Herkunftsniveau),
aber nicht ob `evidence.path` tatsächlich existiert.

- **Betroffen:** Alle Claims mit `evidence_status: repo_local` in `evidence-pack.yml`.
- **Konsequenz:** `PASS`-Claims können auf nicht-existierende Pfade zeigen, ohne
  dass der Validator blockiert.
- **Bereits geprüft in** `validate_run_bundle.py` (R5: `repo_local`-Pfade in
  `evidence-pack.yml` werden auf Dateiexistenz geprüft). Aber `validate_claim_evidence.py`
  läuft auch standalone (CLI + Make-Target `validate-claim-evidence`).

**Benötigte Änderung:**
- Ziel-Datei: `scripts/docmeta/validate_claim_evidence.py`
- Ziel-Funktion: `semantic_errors_for_claim()`
- Gate: für jeden Evidence-Eintrag mit `status: repo_local` → prüfe ob `path`
  (aufgelöst relativ zu `REPO_ROOT`) existiert. Neue Rule-ID:
  `REPO_LOCAL_EVIDENCE_PATH_NOT_FOUND`.
- **ACHTUNG:** `validate_claim_evidence.py` kennt keinen `run_dir`-Kontext —
  `repo_local`-Pfade werden als repo-root-relativ interpretiert. Das ist konsistent
  mit `validate_run_bundle.py` (dort Zeile 955–963 gleiche Semantik).

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

Folgende drei Checks würden verhindern, dass `task_completion_time_observed`,
`review_friction_count` und `rework_count` erneut als belegt erscheinen, obwohl
sie nur `self_reported` oder `missing_evidence` sind.

### Check C-1 — Timing-Artifact-Kopplung (neu)

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

### Check C-2 — Evidence-Datei-Existenz in validate_claim_evidence.py (B-02)

**Was:** `validate_claim_evidence.py`, `semantic_errors_for_claim()`:
für `evidence.status == "repo_local"` → prüfe ob `REPO_ROOT / evidence.path`
existiert. Neue Rule-ID: `REPO_LOCAL_EVIDENCE_PATH_NOT_FOUND`.

**Ziel-Datei:** `scripts/docmeta/validate_claim_evidence.py`

**Ziel-Claims:** Alle `evidence-pack.yml`-Claims mit `repo_local`-Evidence-Pfaden

**Warum minimal:** `validate_run_bundle.py` prüft das bereits (Zeilen 944–963),
aber `validate_claim_evidence.py` prüft es nicht standalone. Lücke schließen
ohne neue Infrastruktur.

**Risiko:** `validate_claim_evidence.py` bekommt Zugriff auf das Dateisystem
(bisher nur YAML-Parsing). Tests müssen mit temporären Fixtures angepasst werden.
Führt keinen Breaking Change in bestehenden Runs ein, weil bestehende
`repo_local`-Evidence-Pfade bereits existieren (sonst hätte `validate_run_bundle.py`
blockiert).

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

### Option A — Kleinster sicherer Patch: Check C-2 (Datei-Existenz in validate_claim_evidence.py)

**Ziel-Dateien:**
- `scripts/docmeta/validate_claim_evidence.py` — neue Prüfung in `semantic_errors_for_claim()`
- `scripts/docmeta/test_validate_claim_evidence.py` — neue Fixture-Tests für den Fall "repo_local, Datei fehlt"

**Ziel-Claims:** `evidence.status == "repo_local"` in beliebiger `evidence-pack.yml`

**Validator-Gate:** Rule `REPO_LOCAL_EVIDENCE_PATH_NOT_FOUND` blockiert PASS und
non-PASS-Claims gleichermaßen (nicht nur PASS — Datei-Existenz ist immer Pflicht
wenn `repo_local` behauptet wird).

**Risiko (niedrig):** Kein Breaking Change. `validate_run_bundle.py` prüft
dasselbe bereits. Konvergenz, keine Regression.

**Nutzen (mittel):** Schließt die PR-5-Checklisten-Lücke `[ ] No PASS without existing/archived evidence file.`
Standalone-CLI (`validate-claim-evidence`) wird vollständig.

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

## 5. Stop-Kriterium dieser Diagnose

**Erfüllt:** Für jeden der drei Patch-Optionen sind benannt:
- Exakte Ziel-Dateien (s. §4)
- Exakte Ziel-Claims / Ziel-Felder (s. §2 und §3)
- Validator-Gate-ID (s. §3 und §4)

**Nicht erfüllt — erfordert weitere Sichtung vor Patch-Start:**
- Tatsächlicher Zustand von `tests/fixtures/claim_evidence/` (Option C) — Dateisystem
  nicht ausgelesen.
- Tatsächlicher Zustand der `evidence-pack.yml`-Dateien in run-007 bis run-010 bzgl.
  `self_reported`-Evidence (für Check C-3) — YAML-Inhalt nicht ausgelesen.
- Entscheidung, ob CI-Global-Enforce für `review_evidence_artifact` (§2.3) als
  eigener PR gewertet wird oder als Teil eines der obigen Optionen.

**Kein Patch vor Entscheidung über:**
- Welche(r) der drei Optionen (A, B, C) zuerst umgesetzt wird.
- Ob Option A + B kombiniert oder sequenziell umgesetzt werden.
