---
title: "Playbook — PR Run Evidence Pack"
status: draft
canonicality: exploratory
relations:
  - type: references
    target: ../blueprints/blueprint-evidence-control-plane-v1.md
  - type: references
    target: evidence-control-plane-roadmap-checklist.md
  - type: references
    target: ../policies/pr-run-evidence-policy.md
  - type: references
    target: ../policies/artifact-boundary-policy.md
---

# Playbook — PR Run Evidence Pack

> Diese Playbook ist nicht technisch enforced.
> Sie aktiviert kein Schema, keinen Validator, keine Make/CI-Gate.
> Sie beschreibt nur die operative Zielstruktur für spätere Evidence-Packs in experimentellen PRs.

## Zweck

Experimentelle PR-Runs sollen ihre Claims an nachvollziehbare, archivierte Evidenz binden.

Das Ziel ist nicht „bessere Agenten", sondern **weniger unbelegte PASS-Claims**.

## Zielstruktur für Evidence-Packs

Pro experimenteller PR (mind. PR 3 der Evidence-Control-Plane aufwärts) wird eine Evidence-Pack-Struktur angelegt:

```text
artifacts/<run-id>/
  evidence-pack.yml
  evidence-pack/
    changed-files.txt
    pr-body.md
    pr-metadata.json
    test-output.txt
    make-validate.txt
    ci-output.txt
    agent-critic-output.md
```

### Zweck jeder Komponente

| Komponente | Zweck |
|---|---|
| `evidence-pack.yml` | Manifest: Verzeichnis, Checksummen, Erfassungs-Metadaten |
| `changed-files.txt` | Repo-lokale Kurzliste geänderter Dateien (nicht vollständiger Diff) |
| `pr-body.md` | PR-Body zum Zeitpunkt der Erfassung |
| `pr-metadata.json` | PR-Nummern, Autor, Labels, Reviews, Refs |
| `test-output.txt` | `make test` oder `pytest` STDOUT/STDERR (gekürzt auf <1MB) |
| `make-validate.txt` | Vollständige oder gekürzte `make validate` Ausgabe |
| `ci-output.txt` | Workflow-Zusammenfassung oder gekürzte CI-Logs |
| `agent-critic-output.md` | Auditor-/Critic-Agent-Ausgabe oder Zusammenfassung |

---

## Missing-Evidence-Varianten

Wenn Artefakte nicht vorhanden sind, werden Abwesenheitsnachweise angelegt:

```text
evidence-pack/
  ci-output.MISSING_EVIDENCE.txt
  agent-critic-output.MISSING_EVIDENCE.md
  pr-metadata.MISSING_EVIDENCE.json
```

**Wichtig:**

- Missing-Evidence-Dateien sind Abwesenheitsnachweise.
- Sie beweisen keinen Erfolg.
- Sie dürfen **keinen PASS-Prozessclaim stützen**.
- Ein PASS-Claim braucht die tatsächliche Evidence-Datei, nicht deren Abwesenheitsdokumentation.

---

## Evidence-Status-Vokabular (geplant für PR 4)

Das folgende Vokabular ist **geplant** und wird als Schema/Validator in PR 4 implementiert.  
PR 3 dokumentiert es nur operativ.

```yaml
evidence_status:
  allowed_for_pass:
    - repo_local
      # Artefakt existiert lokal im Evidence-Pack
    - archived_external
      # Extern archiviert mit Checksumme und Quelle dokumentiert
    - ci_artifact
      # Von CI-System archiviert oder aggregiert
    - derived_from_auditor_output
      # Aus strukturiertem Auditor-/Critic-Output extrahiert

  not_allowed_for_pass:
    - missing_evidence
      # Dokumentierte Abwesenheit
    - external_unverified
      # Externe Quelle ohne Checksumme oder Quelle ungeprüft
    - self_reported
      # Nur im PR-Body behauptet, keine externe Bestätigung
    - unknown
      # Status unklar oder fehlerhafte Kategorie
```

---

## Claim-Regeln

Die folgenden Regeln sind **geplant** für PR 5 (Claim-Evidence-Validator).  
PR 3 dokumentiert sie operativ.

### 1. Kein Testcount-Claim ohne test-output.txt

**Claim:** „101/101 Tests bestanden"  
**Erforderliche Evidence:** `evidence-pack/test-output.txt`  
**Zulässiger Status:** `repo_local`  
**Verboten:** `self_reported`

### 2. Kein CI-success-Claim ohne archivierte CI-Evidence

**Claim:** „CI workflow passed"  
**Erforderlich:** `evidence-pack/ci-output.txt` oder `MISSING_EVIDENCE`  
**Wenn MISSING_EVIDENCE:** Nur mit explizitem Missing-Evidence-Marker erlaubt  
**Verdict für MISSING:** nicht PASS, sondern `MISSING_EVIDENCE`

### 3. Kein „make validate" Claim ohne Command-Output-Artefakt

**Claim:** „make validate bestanden"  
**Erforderlich:** `evidence-pack/make-validate.txt`  
**Status:** `repo_local`

### 4. Kein Critic-/Auditor-Usage-Claim ohne archiviertes Agent-Output-Artefakt

**Claim:** „Experiment mit Critic-Agent durchlaufen"  
**Erforderlich:** `evidence-pack/agent-critic-output.md` oder strukturierte Auditor-Ausgabe  
**Status:** `derived_from_auditor_output` oder `repo_local`

### 5. PR-Body-Claims müssen auf Evidence-Artefakte verweisen

**Claim:** Quantitativer oder prozessualer Claim im PR-Body  
**Erforderlich:**
- Explizite Referenz auf Evidence-Artefakt, z.B.: `[Evidence: evidence-pack/test-output.txt]`
- Oder explizite Kennzeichnung: `[no evidence archived]` (mit Begründung)

**Verboten:** Unkommentiertes Fehlen jeglicher Evidence-Dokumentation

### 6. Status `self_reported` darf keinen PASS-Prozessclaim begründen

**Claim:** „Testlauf erfolgreich" (nur im PR-Body, keine weitere Evidenz)  
**Verdict:** `self_reported`, nicht PASS  
**Konsequenz:** Blockierend für Merge bei PR 5+

---

## Beispiele

### Beispiel 1 — Zulässiger PASS-Claim

```yaml
claim_id: "test-101-pass"
text: "101/101 Tests bestanden"
type: "test_result"
verdict: "PASS"
evidence:
  - path: "evidence-pack/test-output.txt"
    status: "repo_local"
    captured_at: "2026-05-03T14:22:00Z"
```

**Begründung:**  
- Evidence existiert lokal
- Datei enthält vollständigen Test-Output
- Status ist `repo_local` (zulässig für PASS)
- Claim ist über Artefakt nachvollziehbar

---

### Beispiel 2 — Missing Evidence

```yaml
claim_id: "ci-workflow-missing"
text: "CI workflow bestanden"
type: "ci_result"
verdict: "MISSING_EVIDENCE"
evidence:
  - path: "evidence-pack/ci-output.MISSING_EVIDENCE.txt"
    status: "missing_evidence"
    reason: "CI workflow executed but logs not captured in this run"
    captured_at: "2026-05-03T14:22:00Z"
```

**Begründung:**

- Missing-Evidence-Marker dokumentiert Abwesenheit
- Claim wird nicht mit PASS gelöst
- Verdict ist explizit `MISSING_EVIDENCE`, nicht PASS
- Transparenz über Lückenhaftigkeit

---

### Beispiel 3 — Verbotener PASS-Claim

```yaml
claim_id: "test-result-self-reported"
text: "101/101 Tests bestanden"
type: "test_result"
status: "self_reported"
# Kein evidence-Feld, keine Dateiablage, keine externe Bestätigung
verdict: "SELF_REPORTED"
```

**Begründung:**

- Evidence-Status `self_reported`
- Keine archivierte Quelle
- Kein PASS erlaubt (blockiert ab PR 5)
- Muss entweder in `repo_local` umgewandelt oder als `MISSING_EVIDENCE` explizit gemacht werden

---

## Große Artefakte: Externe Referenzierung (geplant für PR 7)

Artefakte, die größer als **1 MB** sind, werden nicht vollständig repo-lokal committet.

Lokal bleiben nur:

```yaml
large_artifact:
  name: "complete-ci-logs"
  summary: "Full GitHub Actions workflow output, 45 MB"
  sha256: "abc123def456..."
  source:
    url: "https://github.com/heimgewebe/vibe-lab/runs/12345678"
    type: "github_actions_workflow"
  captured_at: "2026-05-03T14:22:00Z"
  retention_note: "Expires after 180 days"
```

**Regel (geplant für PR 7):**

- Vollständige PR-Diffs werden nicht committed (nur Dateiliste)
- Große CI-Logs werden nicht committed (nur Hash und Ref)
- API-Dumps werden nicht committed (nur Struktur und Checksumme)
- Screenshots werden nicht committed (nur beschreibende Metadaten)
- Lange Transkripte werden gekürzt oder extern referenziert

---

## Abgrenzung

### Scope und Grenzen dieses Playbooks

- **Gültig für:** Experimentelle PRs ab PR 3 der Evidence-Control-Plane-Roadmap
- **Noch nicht gültig für:** Historische Runs vor dieser Playbook-Einführung
- **Keine rückwirkende Umbewertung:** Historische Runs müssen nicht retrofittet werden
- **Keine harten Regeln (noch):** Enforcement erfolgt erst ab PR 5+

### Was dieses Playbook NICHT leistet

- Keine technische Blockierung in CI (kommt PR 5+)
- Kein Schema-Enforcement (kommt PR 4+)
- Kein Validator-Gate (kommt PR 5+)
- Keine Aussage über Agent/Skill-Wirksamkeit
- Keine Aktivierung von Makefile-Targets
- Keine neuen Experiment-Runs

### Übergänge zu zukünftigen PRs

| PR | Artifact | Enforcement |
|---|---|---|
| PR 3 (dieses Playbook) | Operational guide | Keine |
| PR 4 | JSON-Schema | Keine CI-Integration |
| PR 5 | Python Validator | First CI-Gate |
| PR 6 | Run-Bundle-Schema | Warn-Modus |
| PR 7 | PR-Scope-Guard | Blockierend |

---

## Nächste Schritte nach PR 3

1. **PR 4:** Schema `schemas/run-evidence-pack.v1.schema.json` mit Fixtures
2. **PR 5:** Validator `scripts/docmeta/validate_claim_evidence.py` mit Make/CI-Integration
3. **PR 6:** Run-Bundle-Erweiterung für Evidence-Pack-Verweise
4. **PR 7:** Artifact-Boundary-Guard gegen große Dateien

Bis dahin bleibt die Evidence-Control-Plane operativ dokumentiert, aber nicht technisch enforced.
