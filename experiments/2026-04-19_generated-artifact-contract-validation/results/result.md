---
title: "Experiment-Ergebnis: Generated Artifact Contract Validation"
status: draft
canonicality: operative
---

# result.md — Experiment-Ergebnis

## Zusammenfassung

**Stand nach PR-62 (Run-003):** Zwei unabhängige PR-Runs sind dokumentiert (Run-001 / PR-58 und Run-003 / PR-62). Die Hypothese ist jetzt vorsichtig beurteilbar — noch kein Baseline-Vergleich, aber erste Messkontraste liegen vor.

Run-001 (PR-58) zeigte ausgeprägte In-PR-Friction: drei canonical-Regenerationszyklen für `doc-index.md` innerhalb eines einzigen PRs (path resolution bug + .venv-Leck). Run-003 (PR-62) war der erste saubere End-to-End-Lauf: keine CI-Blocking-Failures, kein Fix-Zyklus, Determinismus bestätigt.

## Beobachtungen

> Gestützt auf evidence.jsonl. Keine Schlüsse hier — die gehören in ## Deutung.

### Wirksamkeit (Effektivität)
Die Klassentrennung `canonical/derived/ephemeral` ist im PR-Diff auswertbar. In PR-58 waren betroffen:
- 2 canonical (docs/_generated/doc-index.md, docs/_generated/system-map.md)
- 1 derived (docs/_generated/orphans.md)
- 1 ephemeral (docs/_generated/epistemic-state.md)

In PR-62 waren betroffen:
- 0 canonical (doc-index.md, system-map.md: unverändert)
- 1 derived (docs/_generated/orphans.md)
- 0 ephemeral

### Reibung (Aufwand)

**Run-001 / PR-58** (in-PR, nicht als separater Run):
- **Commit d561893**: Canonical artifact `doc-index.md` und `system-map.md` zweites Mal regeneriert nach Bug in `resolve_generated_artifact_paths.py`.
- **Commit 7c44b07**: `doc-index.md` drittes Mal regeneriert. `.venv`-Verzeichnis fälschlicherweise gescannt. Fix + Regen.
- `ci_blocking_failures`: nicht gemessen. `manual_regen_steps`: nicht gemessen.

**Run-003 / PR-62** (vollständig gemessen):
- `ci_blocking_failures`: 0
- `ci_non_blocking_warnings`: 0
- `manual_regen_steps`: 1 (erster generate-Lauf; zweiter war Determinismus-Check, idempotent)
- `unnecessary_commit_delta`: 0
- `diagnosis_clarity_score`: 5/5

### Diagnosis Clarity
Run-001: nicht gemessen. Run-003: 5/5 (sauber, keine Unklarheit über Fehlerursachen).

## Deutung

> Interpretation, explizit als solche markiert.

Run-003 zeigt, dass das canonical/derived/ephemeral-Contract-Modell im Prinzip reibungsarme PRs ermöglicht — aber das ist Interpretation auf Basis eines sauberen Runs. Die Friction in Run-001 war primär generator-bug-bedingt, nicht contract-bedingt. Es ist noch nicht sauber trennbar, ob das Modell Friction reduziert oder nur sichtbar macht.

Der Kontrast (Run-001: mehrere Regenerationszyklen, Run-003: null Failures) ist ein erster Messpunkt. Nicht mehr, nicht weniger.

## Verdict

Vorläufig offen. Zwei unabhängige PR-Runs dokumentiert. Erste Messkontrastdaten liegen vor. Hypothesenprüfung möglich, aber noch nicht belastbar — für ein stabiles Urteil fehlt mindestens ein dritter vergleichbarer Run mit vollständiger Metrikerhebung für alle fünf primären Metriken.

## Lessons Learned

- Canonical artifacts erwiesen sich in Run-001 als anfällig: generator-bugs lösten mehrfache Regenerationszyklen aus.
- Run-003 war der erste vollständig metrik-erfasste saubere Lauf: alle Zielmetriken explizit erhoben, keine Doppelfelder in evidence.jsonl.
- Evidence-Einträge ohne Zusatzfelder (`type`, `event`, `details`, `metrics`) sind lesbarer und reduzieren semantischen Drift.
- Die Determinismus-Prüfung (double-run check) ist reproduzierbar und schnell.

## Nächste Schritte

- Dritten vollständigen vergleichbaren Messlauf erfassen (Run-004 auf eigenem PR)
- Alle fünf Metriken konsistent über alle Runs erfassen: `ci_blocking_failures`, `manual_regen_steps`, `changed_canonical_count`, `diagnosis_clarity_score`, `unnecessary_commit_delta`
- Danach: Wechsel auf `result_assessment` in `decision.yml` prüfen

## Interpretation Budget

> Pflicht bei adopted status / promotion-relevanten Experimenten. Wird befüllt vor Promotion.

### Allowed Claims
- Die Klassentrennung canonical/derived/ephemeral ist im PR-Diff beobachtbar und auswertbar (belegt durch Run-001, PR-58 und Run-003, PR-62).
- In PR-58 wurden canonical artifacts mehrfach (3x) regeneriert — beobachtet, nicht quantitativ ausgewertet.
- In PR-62 wurden null CI-Blocking-Failures beobachtet und alle Metriken vollständig erhoben.
- Run-003 ist der erste vollständig metrik-erfasste saubere Lauf in diesem Experiment.

### Disallowed Claims
- Dass das Contract-Modell CI-Friction reduziert (kein Baseline-Vergleich, zwei Runs mit unterschiedlicher Friction-Ursache).
- Verallgemeinerungen über den PR-Prozess auf Basis von zwei Runs.
- Adoption-Empfehlungen vor mindestens einem weiteren vergleichbaren Run.

### Evidence Basis
- Direkt beobachtet: Run-001 (PR-58), Diff-Klassifikation, In-PR canonical regen × 3 (commits d561893, 7c44b07)
- Nicht gemessen: CI-blocking-failures, manual_regen_steps (explizit), diagnosis_clarity_score, baseline PRs
