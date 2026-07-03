# Repo-Komplettaudit (2026-07-02) — Third Pass

> Rohe Beobachtung. Keine Promotion. Knüpft an
> `raw-vibes/2026-05-05_repo-improvement-audit.md` und
> `raw-vibes/2026-05-18_audit-followup-second-pass.md` an.
> Basis: vollständiger Lauf des Guard-Stacks (`make agent-check`,
> `make validate`, `make generate`), Link-Prüfung aller Markdown-Dateien,
> Abgleich Steuerungsdokumente ↔ Schemas ↔ CI ↔ Navigation.
> Operator-Lab-Spur: `experiments/2026-07-01_operator-lab-loop/artifacts/run-016-repo-audit-third-pass/run-card.yml`.

## Prüfumfang und Methode

- `make agent-check`: OK.
- `make validate`: grün mit einer Umgebungsausnahme (siehe R4) —
  alle Schema-, Relations-, Contract-, Fixture-, Ratchet- und
  Regressionstest-Gates bestanden.
- `make generate`: deckte Drift in drei Diagnose-Artefakten auf (F1).
- Eigener Link-Checker über alle `*.md`: 0 kaputte relative Links.
- Abgleich: CONTRIBUTING/README/index/roadmap gegen `schemas/*`,
  `.vibe/*`, `.github/workflows/*`, Orphans-/Taxonomie-Diagnose.

## Was funktioniert (kurz)

- Der Guard-Stack ist konsistent verdrahtet: alle in Makefile und CI
  referenzierten Skripte existieren; Fixture- und Regressionstests laufen grün.
- Keine kaputten relativen Links in der gesamten Markdown-Oberfläche.
- Promotion-Readiness-Ratchet stabil: 14 tolerierte Frozen-Cases,
  12 validierte Freeze-Einträge, keine neuen Verstöße.
- Die Welle-1-Fixes aus den Audits 2026-05-05/2026-05-18 sind weiterhin intakt.

## Welle A — In diesem Audit behobene Befunde

| # | Befund | Klasse | Fix |
|---|--------|--------|-----|
| F1 | Generierte Diagnose-Artefakte veraltet: `docs/_generated/system-map.md`, `artifact-taxonomy.{md,json}` hinkten dem Stand nach PR #263 (run-010-Dateien) hinterher | Drift generiert↔Quellen | `make generate` regeneriert, Ergebnis committet (kein manueller Edit) |
| F2 | `CONTRIBUTING.md:49` nannte `verdict (adopted / rejected)` für `decision.yml` — kanonisches Schema (`schemas/decision.schema.json`, adoption_assessment) verlangt `adopt \| reject \| defer`; `.vibe/quality-gates.yml` war bereits korrekt | Doku-Drift gegen kanonische Quelle | CONTRIBUTING an Schema angeglichen (kanonisch > operativ) |
| F3 | `doc-freshness-registry` und `bundle-freshness-receipt` werden in CI über eigene Workflows geprüft, waren aber nicht in `make validate` — lokale Validierung deckte weniger ab als CI | Lokal↔CI-Parität | Make-Targets ergänzt und in `validate` eingehängt (spiegelt exakt die CI-Schritte) |
| F4 | Navigationslücken in `docs/index.md`: `policies/agent-reading-protocol.md` (aktiv, normativ), `playbooks/bundle-freshness-receipt.md`, `playbooks/evidence-control-plane-post-pr189-diagnosis.md`, `playbooks/outcome-evidence-replication-series-gate.md` fehlten; Diagnose-Tabelle ohne `artifact-taxonomy.json` | Navigation unvollständig; 2 aktive Docs als unexpected orphans | Einträge + Frontmatter-Relationen ergänzt |
| F5 | `.vibe/intent.md` von keiner Frontmatter-Relation referenziert (unexpected orphan) | Orphan | Referenz in `docs/index.md` (Steuerungsdokumente) ergänzt |
| F6 | `requirements.txt` einziges unklassifiziertes Artefakt der Taxonomie (`unknown=1`); alle übrigen Root-Dateien haben explizite Regeln | Diagnose-Lücke | Taxonomie-Regel (governance / dependency_manifest) ergänzt |
| F7 | Roadmap-Regel §7.3 nicht angewendet: RM-001 ist quellenbelegt erledigt (reconciled 2026-05-29), stand aber weiter in §2 statt im vorgesehenen Abschnitt „§8 Erledigt / Superseded" | Roadmap-interne Inkonsistenz | §8 angelegt, RM-001 mit done + Quellennachweis verschoben |
| F8 | README-Projektstruktur ohne `instruction-blocks/` (Library-Zone laut `repo.meta.yaml`!), `exports/` und `tests/` | Doku unvollständig | Struktur-Diagramm ergänzt |
| F9 | Operator-Lab-Manifest `execution_refs` spiegelte run-009/run-010 nicht (Artefakte existieren seit PR #260/#263) | Manifest ↔ Ist-Zustand | Refs faktenbasiert ergänzt (kein Status-Wechsel), `updated` angehoben |

## Welle B — Berichtete Befunde (menschliche Entscheidung nötig, nicht umgesetzt)

| # | Befund | Warum nicht umgesetzt | Vorschlag |
|---|--------|----------------------|-----------|
| R1 | `requirements.txt` ist ungepinnt (PyYAML, jsonschema, rfc3339-validator ohne Version) — CI-Läufe sind nicht bitgenau reproduzierbar | Pinning-Strategie ist eine Wartungs-/Governance-Abwägung | Entweder exakte Pins + Update-Routine oder bewusstes Offenlassen dokumentieren |
| R2 | `.cursor/rules/*` wird in `repo.meta.yaml`, `AGENTS.md`, `agent-policy.yaml`, `.vibe/constraints.yml` als generierter Pfad geführt, existiert aber nirgends; kein Generator erzeugt ihn | Kanonische Quellen sind ausschließlich handgepflegt (Verbot 1) | Mensch entscheidet: Pfad aus kanonischen Quellen entfernen oder Generator-Ziel nachziehen |
| R3 | Aus Audit 2026-05-05 weiter offen: globaler `errors = []`-State in `validate_schema.py:66`; duplizierte YAML/Schema-Loader in 10+ Skripten (kein gemeinsames `_validators.py`); `contracts/system_decision.schema.json` ohne `schema_version` | Bewusst zurückgestellte Refactors mit Regressionsrisiko (siehe Second Pass) | Als eigener kleiner Refactor-PR mit Testabdeckung |
| R4 | `validate-model-lab-access-policy-tests` (Live-Probe) läuft nur, wenn `/usr/bin/python3` innerhalb der Sandbox auflösbar ist; in Containern mit `/etc/alternatives`-Symlink bricht die Symlink-Kette (Exit 127). GitHub-CI (ubuntu-latest) ist nicht betroffen | Run-004-Bundle ist hash-eingefroren; jede Anpassung wäre Freeze-Drift | Bekannte Umgebungsgrenze; falls Remote-Umgebungen relevant werden: Freeze-bewusste Neubindung durch Menschen |
| R5 | Taxonomie-Fallback-Share 54,2 % > 50 %-Advisory-Schwelle (CI-Warnung) — über die Hälfte aller Artefakte wird nur durch Catch-all-Regeln klassifiziert | Regel-Verfeinerung ist inhaltliche Taxonomie-Arbeit, nicht mechanisch | Catch-all-Regeln für `experiments/*/artifacts/*`-Klassen schrittweise präzisieren oder Baseline begründen |
| R6 | 83 unexpected orphans, überwiegend Experiment-Artefakte (`premortem-prompting`, `agent-task-validity`, …) | Bereits im Second Pass als Architektur-Entscheidung markiert (Expected-Orphan-Allowlist) | `orphan-policy.yml`-Muster pro Artefaktklasse oder bewusstes Tolerieren dokumentieren |
| R7 | CODEOWNERS wirkt nur mit aktivierter Branch Protection (im File selbst dokumentiert); Wirksamkeit ist repo-seitig nicht prüfbar | GitHub-Settings, nicht Repo-Inhalt | Einmalig verifizieren: Branch Protection für `main` mit Code-Owner-Review |

## Nicht-Befunde (geprüft, in Ordnung)

- Alle Makefile-/CI-Skriptreferenzen existieren; keine toten Targets.
- README-Schnellstart stimmt mit `.github/ISSUE_TEMPLATE/` und
  `PULL_REQUEST_TEMPLATE/promotion.md` überein.
- `CONTRIBUTING.md:74` (`adopted / rejected` als Experiment-**Status**) ist
  korrekt — Manifest-Schema-Enum bestätigt; nur der `decision.yml`-**Verdict**
  (F2) war falsch.
- Export-Parität (collision/orphan/missing) grün; Exports deterministisch.
- Doc-Freshness-Registry: 5 Einträge, alle valide.
- Anker-Dateien (CLAUDE.md, GEMINI.md, CONVENTIONS.md, .aider.conf.yml)
  konsistent zueinander und zu AGENTS.md.

## Plan / Reihenfolge-Empfehlung für Welle B

1. **R2** (kanonischer Geist-Pfad `.cursor/rules/*`) — kleinster Eingriff,
   nur Mensch; beseitigt eine dauerhaft irreführende Angabe in der Verfassung.
2. **R1** (Dependency-Pinning) — eine Zeile Entscheidung, direkter
   Reproduzierbarkeitsgewinn für alle Gates.
3. **R3** (Refactor-Paket) — ein PR: `_validators.py` einführen,
   `validate_schema.py`-State kapseln, `schema_version` in
   `system_decision.schema.json` nach Migration der zwei Bestands-Decisions.
4. **R5/R6** (Diagnose-Schärfung) — gemeinsame Session: Taxonomie-Regeln
   und Orphan-Allowlist in einem Zug, da beide dieselben Artefaktklassen betreffen.
5. **R7** (Branch Protection) — einmaliger Settings-Check.

## Epistemische Grenzen dieses Audits

- Dieses Audit belegt Konsistenz der geprüften Oberflächen zum Stichtag,
  nicht inhaltliche Qualität von Experimenten oder Praktiken.
- Kein Status-, Promotion- oder Adoption-Urteil wurde getroffen oder verändert.
- Die Welle-A-Fixes sind mechanisch quellengebunden (Schema→Doku,
  CI→Makefile, Ist-Artefakte→Manifest-Refs, Roadmap-Eigenregel §7.3);
  sie erzeugen keine neuen fachlichen Wahrheiten.
