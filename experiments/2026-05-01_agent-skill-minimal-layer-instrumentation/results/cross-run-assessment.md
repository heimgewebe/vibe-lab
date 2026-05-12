---
title: "Cross-Run-Auswertung: Agent/Skill Minimal Layer Instrumentation"
status: draft
canonicality: operative
triggered_by: user-request-2026-05-10-pr11-cross-run-assessment
relations:
  - type: references
    target: evidence.jsonl
  - type: references
    target: result.md
---

# Cross-Run-Auswertung — Agent/Skill Minimal Layer Instrumentation

## 0. Scope-Deklaration und Vorbedingungen

**Vergleichsbasis:** run-002, run-005, run-006 (`comparability_verdict: reference_only` bzw. `comparable`)

**Ausgeschlossen:** run-003, run-004 (`comparability_verdict: not_comparable` — PR-10-Rehearsal-Kontext, kein `independent_task_or_pr_ref`)

**Nicht einbezogen:** run-001 (andere Instrumentierungsklasse: `promotion-readiness-prepared-without-measurement`, strukturell außerhalb der Vergleichsbasis für `controlled-agent-skill-run`)

**Pflichtlektüre-Lücke:** `docs/policies/agent-reading-protocol.md` — **FEHLT**: Datei existiert nicht im Repo.
Nötig für: Prüfung ob Lese-Protokoll-Pflicht für dieses Assessment eingehalten wurde.
Diese Prüfung kann nicht durchgeführt werden. Keine Ersatzableitung.

---

## 1. Zielhypothese

**Aus manifest.yml:**

> The measurement scaffold can capture comparable PR-level data for the Agent/Skill Minimal Layer without making an effect claim.

**Was konkret getestet wird:**

Ob das Messgerüst (run-bundle-Artefakte + evidence-reconciliation-auditor + comparability.yml) über mehrere unabhängige Runs hinweg konsistent und vergleichbar Daten erfasst — ohne dabei eine Aussage über den Nutzen oder die Wirkung der Agent/Skill-Schicht zu machen.

**Was explizit NICHT getestet wird:**

- Ob die Agent/Skill-Schicht Fehler reduziert
- Ob die Agent/Skill-Schicht review-Friktion senkt
- Ob die Agent/Skill-Schicht Rework verhindert
- Ob irgendein Outcome kausal auf die Schicht zurückführbar ist

**Operative Friktion, die das Scaffold adressiert:**

Unvollständige oder nicht-vergleichbare Run-Archive, die Cross-Run-Vergleiche verhindern. Das Scaffold soll diese Friktion auf Ebene der Artefaktstruktur beheben — nicht auf Ebene der Ausführungsqualität.

---

## 2. Gegenhypothesen

Jede Gegenhypothese wird tatsächlich geprüft, nicht pro forma behandelt.

### A. Scaffold-PASS ist nur Operator-/Prompt-Effekt

**Hypothese:** Die konsistenten PASS-Verdicts entstehen nur deshalb, weil die Runs durch dieselbe Anweisung gesteuert wurden — nicht weil das Scaffold strukturell belastbar ist.

**Prüfung:** Nicht widerlegbar. Alle drei Runs folgen denselben Scaffold-Anweisungen. Es gibt keinen Vergleichspunkt ohne diese Anweisungen. Der Befund ist: diese Gegenhypothese kann nicht ausgeschlossen werden.

**Status: unresolved**

### B. Scaffold-PASS ist nur Fallselektion

**Hypothese:** Die gewählten Tasks sind systematisch einfacher als repräsentative Arbeit — deshalb keine Failures.

**Prüfung:** Teilweise prüfbar. Run-002 ist mittlere Komplexität (Preflight-Diagnose, mehrere Artefakttypen). Run-005 und Run-006 sind explizit kleine Validator-Test-Hardening-Tasks. Die Vergleichsbasis ist task-homogen innerhalb von runs 005/006 (gleicher Task-Typ, gleiche Kategorie). Es gibt keinen Run mit hoher Komplexität, mit ambiguem Scope, mit Zeitdruck oder mit konkurrierenden Anforderungen. Fallselektion-Bias ist vorhanden und nicht ausgeschlossen.

**Status: nicht_widerlegt** — Fallselektion-Bias ist strukturell vorhanden.

### C. Scaffold-PASS ist nur Bewertungsbias

**Hypothese:** Auditor und Executor sind teilweise identisch (claude-sonnet-4-6 beides) — keine echte Unabhängigkeit.

**Prüfung:** Direkt prüfbar aus den run.yml-Provenienz-Feldern.

| Run | Executor | Auditor-Executor |
|---|---|---|
| run-002 | `local:claude-sonnet-4-6` | `claude-sonnet-4-6` |
| run-005 | `copilot-coding-agent:gpt-5.3-codex` | `copilot-coding-agent:gpt-5.3-codex` |
| run-006 | `claude-code:claude-sonnet-4-6` | `claude-code:claude-sonnet-4-6` |

In allen drei Runs ist Auditor-Executor == Executor. Kein einziger Run hat einen unabhängigen externen Auditor. Bewertungsbias kann nicht ausgeschlossen werden. Provenienz-Level aller Runs: `self_reported`.

**Status: nicht_widerlegt** — Selbst-Auditierung in allen Runs; kein unabhängiger Reviewer für Metrik-Erhebung.

### D. Scaffold-Funktion ist nicht stabil replizierbar

**Hypothese:** Die PASS-Verdicts replizieren sich nicht über echte Task-Varietät hinweg.

**Prüfung:** Begrenzt prüfbar. Drei PASS-Verdicts vorliegen. Jedoch: runs 005 und 006 sind dieselbe Task-Klasse (small validator-test hardening). Das ist kein echter Replizierbarkeitstest über Task-Varietät — es ist eine Reproduktion innerhalb einer engen Task-Klasse. Ob das Scaffold für komplexe, ambigue oder multi-stage Tasks PASS produziert, ist ungetestet.

**Status: teilweise_repliziert** — Scaffold funktioniert für kleine, klar-gescopte Tasks. Keine Evidenz für breitere Task-Klassen.

### E. PASS ist nur bessere Dokumentation, nicht bessere Ausführung

**Hypothese:** Das Scaffold erzeugt gut strukturierte Artefakte, ohne dass die tatsächliche Ausführungsqualität steigt.

**Prüfung:** Diese Gegenhypothese ist strukturell korrekt und durch die Hypothese selbst vorgegeben: das Experiment testet explizit nur das Messgerüst, nicht die Ausführungsqualität. Die Gefahr liegt in der Verwechslung: "vollständige Artefakte" ≠ "gute Ausführung". `review_friction_count` und `rework_count` — die einzigen Metriken, die Ausführungsqualität indirekt sichtbar machen könnten — sind in allen drei vergleichbaren Runs `null (missing_evidence)`.

**Status: strukturell bestätigt** — Das Scaffold liefert dokumentarische Konsistenz. Ob dies Ausführungsqualität widerspiegelt: unbekannt und durch die vorliegenden Daten nicht beantwortbar.

---

## 3. Vergleichsmatrix

### Run-002 (reference anchor)

| Dimension | Befund |
|---|---|
| Task | Evidence-capture + Preflight-Diagnose (Measurement-System-Readiness für PR#9) |
| Failure Surface | Unvollständige Artefaktstruktur ohne evidence-pack-Kopplung |
| Intervention | Erste vollständige evidence-pack-Kopplung; alle 4 Auditor-Claims PASS |
| Validator/Guard | evidence-reconciliation-auditor, make validate, test_validate_run_bundle.py, test_validate_claim_evidence.py, test_validate_pr_scope.py |
| Was verbessert | Artefaktstruktur-Vollständigkeit; comparability-Baseline etabliert |
| Was NICHT verbessert | review_friction_count: null; rework_count: null; changed_files_artifact: null (added in later runs) |
| Gegenhypothesen geprüft | E (strukturell korrekt) |
| Gegenhypothesen nicht geprüft | A, B, C, D (kein Referenzpunkt für Vergleich) |
| Scope Drift | 0 (repo_local) |
| Missing Evidence | review_friction_count, rework_count, changed_files_artifact, unabhängige Zeitmetrik |

### Run-005

| Dimension | Befund |
|---|---|
| Task | Small Validator-Test-Hardening: Windows-Absolute-Path-Guard (task:validator-test-windows-absolute-path-guard) |
| Failure Surface | Fehlender changed_files_artifact-Verweis in comparability.yml (Lücke aus run-002) |
| Intervention | changed_files_artifact-Pflichtfeld eingeführt; changed-files.txt archiviert; comparability.yml claim-005 hinzugefügt |
| Validator/Guard | evidence-reconciliation-auditor (5 claims inkl. claim-005 für comparability), make validate |
| Was verbessert | changed_files_artifact jetzt archiviert und im Auditor-Verdict verifiziert |
| Was NICHT verbessert | review_friction_count: null; rework_count: null; task_completion_time_observed: null |
| Gegenhypothesen geprüft | D (partial: scaffold hält für kleine Tasks) |
| Gegenhypothesen nicht geprüft | A (kein Kontrollpunkt), C (Selbst-Auditierung) |
| Scope Drift | 0 (repo_local) |
| Missing Evidence | review_friction_count, rework_count, task_completion_time_observed |

### Run-006

| Dimension | Befund |
|---|---|
| Task | Small Validator-Test-Hardening: Cross-Run changed_files_artifact Path-Regression (task:validator-test-cross-run-changed-files-artifact-path-guard) |
| Failure Surface | Regressionsfall für Cross-Run-Pfadprüfung des changed_files_artifact |
| Intervention | Regressionstest hinzugefügt; Artefaktstruktur identisch zu run-005 |
| Validator/Guard | Gleich wie run-005 |
| Was verbessert | Regressionstest für Cross-Run-Pfadfall |
| Was NICHT verbessert | Gleich wie run-005: review_friction_count null, rework_count null, task_completion_time_observed null |
| Gegenhypothesen geprüft | D (partial: zweite Instanz derselben Task-Klasse) |
| Gegenhypothesen nicht geprüft | A (kein Kontrollpunkt), C (Selbst-Auditierung); B strukturell verstärkt (zweiter run der gleichen Task-Klasse) |
| Scope Drift | 0 (repo_local) |
| Missing Evidence | Gleich wie run-005: review_friction_count, rework_count, task_completion_time_observed |

### Task-Homogenitätsproblem

Run-005 und Run-006 sind aus derselben Task-Klasse: kleine, scharf-gescopte Validator-Test-Hardening-Aufgaben. Das erzeugt eine Cluster-Struktur statt echter Diversität:

- 1/3 Runs: mittlere Komplexität (run-002)
- 2/3 Runs: kleine Komplexität, gleiche Kategorie (run-005, run-006)

Dieser Cluster ist kein Beweis für Scaffoldrobustheit über Task-Typen hinweg. Er zeigt, dass das Scaffold in einem schmalen Task-Korridor konsistent funktioniert.

---

## 4. Reproduzierbarkeit

### Scaffold-Artefaktstruktur

**repliziert** — Alle drei Runs produzieren vollständige run-bundle-Artefakte (run.yml, measurement.yml, auditor-output.yml, evidence-pack.yml, comparability.yml). Die Struktur ist konsistent.

### Metrik-Abdeckung (5 von 8 Metriken)

**repliziert** — scope_drift_count, unsupported_claim_count, missing_locator_count, validation_gap_count, false_block_count sind in allen drei Runs mit `repo_local` oder `derived_from_auditor_output` evidenziert und konsistent 0.

### Metrik-Abdeckung (3 von 8 Metriken: review_friction, rework, timing)

**nicht repliziert** — review_friction_count und rework_count sind in allen drei Runs `null (missing_evidence)`. task_completion_time_observed ist in run-002 `self_reported` (~60 min), in runs 005 und 006 `null (missing_evidence)`. Diese Lücke ist persistent, nicht zufällig.

Begründung: review_friction_count und rework_count setzen external review events voraus (PR-Kommentare, identifizierbare Rework-Commits). Diese Events werden nicht automatisch archiviert. Das Scaffold hat keine Mechanik, diese Daten zu erfassen — weder durch den Auditor noch durch make validate.

### Scaffold-Robustheit über Task-Klassen

**unklar** — Zwei von drei vergleichbaren Runs sind aus derselben Task-Klasse. Breitere Replikation nicht belegt.

---

## 5. Promotion Blocker

### Blocker für result_assessment

- **review_friction_count fehlt in allen 3 Runs** — nötig für: jede Aussage über review-Prozess-Auswirkung der Schicht
- **rework_count fehlt in allen 3 Runs** — nötig für: jede Aussage über Rework-Reduktion
- **task_completion_time_observed: 2/3 Runs null, 1/3 self_reported** — nötig für: jede komparative Zeitaussage
- **Kein unabhängiger Metrik-Reviewer** — nötig für: Ausschluss von Bewertungsbias (Gegenhypothese C)
- **Task-Diversität fehlt** — nötig für: Replizierbarkeitsnachweis über Task-Klassen hinweg

### Blocker für promotion_readiness

- Kein Nutzbarkeits-Claim möglich (kein outcome-level evidence)
- Kein Kausalclaim möglich (keine Kontrollgruppe, kein Kontrafaktual)
- Keine externe Validierung (alle Evidenz ist repo_local oder self_reported)
- Keine negativen Fälle dokumentiert (kein Run mit Scaffold-Failure, mit FAIL-Verdict, oder mit entdecktem Fehler durch den Auditor)

### Blocker für real usefulness claim

- **review_friction_count fehlt** — direkte Messung fehlender Review-Reibung
- **rework_count fehlt** — direkte Messung von Rework
- **timing ohne Unabhängigkeit** — kein vergleichbares Timing-Signal
- **negative cases fehlen** — kein Run dokumentiert, wo der Auditor einen Fehler gefunden und blockiert hat (false_block_count=0 ohne Auditor-Failure ist kein Kompetenznachweis)
- **task diversity fehlt** — kein komplexer, ambiguoser oder multi-stage Task in der Vergleichsbasis

---

## 6. Final Verdict

**execution_assessment bleibt korrekt.**

Das Scaffold wurde über drei vergleichbare Runs hinweg ausgeführt. Die Artefaktstruktur ist konsistent reproduzierbar. Die Messbedingungen (comparability.yml, evidence-pack.yml, auditor-output.yml) funktionieren nachweisbar für die abgedeckten Metrik-Dimensionen.

**Controlled observation successful, usefulness unresolved.**

Die Hypothese ist für 5/8 Metriken in einem schmalen Task-Korridor bestätigt: Das Scaffold kann vergleichbare PR-level Daten für diese Dimensionen erfassen. Für 3/8 Metriken — darunter die einzigen, die Ausführungsqualität sichtbar machen könnten — ist das Scaffold strukturell unvollständig.

**Further falsification required:**

- Task-Diversitätsnachweis: mindestens ein Run mit komplexem oder ambiguem Task-Scope
- Negativfall-Nachweis: mindestens ein Run, in dem der Auditor tatsächlich einen Fehler identifiziert und blockiert (FAIL-Verdict mit konkretem Artefakt-Rückverweis)
- review_friction_count und rework_count: Archivierungs-Mechanismus für externe Review-Events etablieren
- Unabhängige Metrik-Validierung: Prüfung durch einen Reviewer, der nicht Executor ist

**Nicht erlaubt auf Basis dieser Evidenz:**

- result_assessment
- promotion_readiness
- usefulness claim
- "Das Scaffold funktioniert" als generelle Aussage (es funktioniert für einen schmalen Task-Korridor)

---

## Post run-009 update (2026-05-12)

### Run-009 — Task-Diversity Probe + Independent-Validation Status

| Dimension | Befund |
|---|---|
| Task | Multi-artifact experiment scaffold synthesis: cross-run evidence reading, schema-compliant YAML for 6+ interdependent files, epistemic calibration of verdict and next-steps |
| Task-Cluster | `multi-artifact-scaffold-synthesis` — distinct from `validator-test-hardening` (run-005/006) and `outcome-evidence-pilot` (run-007/008) |
| Executor | `claude-code:claude-sonnet-4-5` |
| Auditor | `evidence-reconciliation-auditor` executed by same session → partial independence only |
| Auditor-Verdict | `CLAIM_NOT_PROVEN` (claim-003: independent audit not proven; claim-002: task-diversity PASS) |
| Timing | `self_reported` with explicit capture_mode, evidence_status, and validation_path note — improvement over run-008 plain-text |
| comparability_verdict | `not_comparable` (partial independence; scoped as probe, not usefulness run) |

### Auswirkung auf die Gesamtbewertung

**Blocker-Fortschritt:**

1. **Task-Diversitätsnachweis (§5):** Teilweise adressiert. Run-009 claim-002 ist PASS: mindestens ein Run existiert nun außerhalb des validator-test-hardening-Clusters. Eine zweite unabhängige Instanz in einer weiteren Task-Klasse wäre für stärkere Replikation nötig.
2. **Unabhängige Metrik-Validierung (§5):** Weiterhin offen. Run-009 dokumentiert explizit CLAIM_NOT_PROVEN für Auditor-Unabhängigkeit statt den Blocker stillschweigend fortzuschreiben.
3. **Timing-Semantik (§5):** Verbessert. timing.txt enthält nun `capture_mode`, `evidence_status: self_reported` und `validation_path`-Notiz. Der Wert bleibt self_reported — kein Upgrade auf repo_local oder external_verified.
4. **Negativfall-Nachweis (§5):** Keine Änderung (run-008 bleibt der Pilot).

**Unverändertes Fazit:**

- `verdict: insufficient_proof` bleibt korrekt.
- Comparable-run-Count bleibt bei 3 (run-002, run-005, run-006).
- `result_assessment`, `promotion_readiness` und Usefulness-Claims sind weiterhin nicht erlaubt.

### Aktualisierte Gegenhypothesen-Lage

| Gegenhypothese | Status nach run-009 |
|---|---|
| A: Scaffold-PASS nur Operator-/Prompt-Effekt | unresolved — unverändert |
| B: Scaffold-PASS nur Fallselektion | abgeschwächt — run-009 ist außerhalb des validator-test-hardening-Clusters, aber Bias nicht ausgeschlossen |
| C: Scaffold-PASS nur Bewertungsbias | nicht_widerlegt — Selbst-Auditierung in allen Runs inkl. run-009 |
| D: Scaffold nicht stabil replizierbar | offen — run-009 belegt Scaffold für einen weiteren Task-Cluster, Replikation bleibt thin |
| E: PASS nur bessere Dokumentation | strukturell bestätigt — unverändert |

---

## Anhang: Fehlende Governance-Referenz

`docs/policies/agent-reading-protocol.md` — referenziert in den Anweisungen für dieses Assessment.

**Status: FEHLT am referenzierten Pfad** — Datei existiert nicht unter `docs/policies/agent-reading-protocol.md`. Repo-weite Suche nach normativem Äquivalent (Lese-Protokoll-Pflicht für Assessments) ergibt keinen kanonischen Ersatz.

Nötig für: Prüfung, ob das Lese-Protokoll für dieses Assessment eingehalten wurde.

Keine Ersatzableitung vorgenommen. Dokumentiert als offene Governance-Lücke, nicht als harter Blocker für dieses Assessment.
