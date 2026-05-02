---
title: "Playbook: Evidence-Control-Plane — Roadmap & Checklist"
status: draft
canonicality: exploratory
created: "2026-05-02"
updated: "2026-05-02"
author: "GitHub Copilot"
triggered_by: "user-request-evidence-control-plane-pr1-2026-05-02"
relations:
  - type: references
    target: "../blueprints/blueprint-evidence-control-plane-v1.md"
  - type: references
    target: "../policies/interpretation-budget.md"
tags:
  - playbook
  - roadmap
  - evidence
  - checklist
  - draft
---

# Playbook: Evidence-Control-Plane — Roadmap & Checklist

> **Statushinweis (zwingend lesen):**
>
> - Diese Datei erzeugt **keine neue Enforcement-Regel**.
> - Sie ersetzt **keinen Blueprint und keine Policy**.
> - Sie trifft **keinen Wirksamkeitsclaim zur Agent/Skill-Schicht**.
> - Sie gilt erst durch **separate validierte PRs** als umgesetzt.
> - Checkboxen sind **geplante Umsetzungsschritte bzw. Scaffold-Status**,
>   kein Beleg aktiver Enforcement-Regeln.
>
> Blueprint: [`docs/blueprints/blueprint-evidence-control-plane-v1.md`](../blueprints/blueprint-evidence-control-plane-v1.md)

---

## Überblick

Diese Roadmap gliedert die Umsetzung der Evidence-Control-Plane in abgeschlossene,
prüfbare PRs. Jeder PR ist eigenständig validierbar; kein PR setzt spätere PRs voraus,
um seinen eigenen Scope zu erfüllen.

**Wichtig:** Abgehakte Punkte (✅) bedeuten nur, dass der jeweilige Scaffold-Schritt
abgeschlossen ist. Sie bedeuten **nicht**, dass:
- die Evidence-Control-Plane aktiv oder wirksam ist,
- Claims technisch blockiert werden,
- Policy, Schema, Validator oder CI existieren,
- Agenten oder Skills messbar beeinflusst werden.

---

## PR 1 — Blueprint + Roadmap + Navigation Scaffold

> Scope: Reine Dokumentations- und Navigationsstruktur. Kein Code, keine Policy,
> kein Schema, kein Validator, keine Experiment-Runs.

- [x] `docs/blueprints/blueprint-evidence-control-plane-v1.md` angelegt.
- [x] Nicht-Ziele explizit dokumentiert: kein Agent/Skill-Wirksamkeitsclaim.
- [x] Architekturskizze und Falsifikationskriterien im Blueprint dokumentiert.
- [x] Diese Roadmap gegen Blueprint gespiegelt und angelegt.
- [x] `docs/index.md` auf neue Blueprint- und Playbook-Dokumente verlinkt.

**Was PR 1 ausdrücklich NICHT leistet:**
- Kein aktives Enforcement
- Keine Policy-Implementierung
- Kein Schema
- Kein Validator
- Keine CI-Erweiterung
- Kein Experiment-Run

---

## PR 2 — Policy-only

> Scope: Ergänzung der bestehenden `interpretation-budget.md` oder neue Policy-Datei,
> die PR-Claims an Evidenz koppelt. Kein Validator-Code.

- [ ] Policy-Dokument erstellt oder `interpretation-budget.md` erweitert.
- [ ] Policy beschreibt Pflichtfelder für Claim→Evidenz-Kopplung.
- [ ] Policy ist in `docs/index.md` verlinkt.
- [ ] `make validate` bleibt grün.

---

## PR 3 — Playbook: pr-run-evidence-pack

> Scope: Operatives Playbook, das beschreibt, wie ein Evidence-Pack für einen PR
> erstellt wird. Kein Schema-Enforcement.

- [ ] `docs/playbooks/pr-run-evidence-pack.md` erstellt.
- [ ] Playbook beschreibt Minimalstruktur eines Evidence-Packs.
- [ ] Playbook verlinkt auf Policy (PR 2) und Schema (PR 4, geplant).
- [ ] `make validate` bleibt grün.

---

## PR 4 — Evidence-Pack-Schema + Fixtures

> Scope: JSON Schema für Evidence-Packs. Test-Fixtures für valide und invalide Packs.

- [ ] `schemas/evidence-pack.schema.json` erstellt.
- [ ] Mindestens 2 valide und 2 invalide Fixtures angelegt.
- [ ] Schema gegen bestehende `evidence.jsonl`-Struktur geprüft.
- [ ] `make validate` bleibt grün.

---

## PR 5 — Claim-Evidence-Validator

> Scope: Validator-Skript, das Claim→Evidenz-Kopplung prüft.

- [ ] `scripts/docmeta/validate_claim_evidence.py` erstellt.
- [ ] Validator in `make validate` eingehängt.
- [ ] Tests für valide und invalide Fälle vorhanden.
- [ ] `make validate` bleibt grün.

---

## PR 6 — Run-Bundle-Kopplung

> Scope: Verbindet PR-Run mit Evidence-Pack. Kopplung ist maschinenlesbar.

- [ ] Run-Bundle-Format definiert und dokumentiert.
- [ ] Kopplung gegen Evidence-Pack-Schema (PR 4) validiert.
- [ ] `make validate` bleibt grün.

---

## PR 7 — PR-Scope-Guard

> Scope: CI-Guard, der Promotions ohne validierte Evidenz blockiert.

- [ ] PR-Scope-Guard implementiert.
- [ ] Guard ist in CI eingehängt.
- [ ] Abschalt-Mechanismus dokumentiert.
- [ ] `make validate` bleibt grün.

---

## PR 8 — PR-Template-Härtung

> Scope: PR-Template erzwingt Evidenz-Pflichtfelder.

- [ ] `.github/PULL_REQUEST_TEMPLATE.md` erweitert.
- [ ] Pflichtfelder für Claim→Evidenz-Kopplung sind sichtbar.
- [ ] Template gegen Policy (PR 2) gespiegelt.

---

## PR 9+ — Kontrollierte Runs / Cross-Run-Assessment

> Scope: Mindestens 3 kontrollierte Runs unter aktiver Evidence-Control-Plane.
> Cross-Run-Assessment nach Abschluss.

- [ ] Mindestens 3 Runs mit Evidence-Pack durchgeführt.
- [ ] Cross-Run-Assessment dokumentiert.
- [ ] Falsifikationskriterien aus Blueprint geprüft.
- [ ] Entscheidung: Blueprint beibehalten, revidieren oder verwerfen.

---

## Offene Fragen

1. Ist das `evidence.jsonl`-Format kompatibel mit dem geplanten Evidence-Pack-Schema
   (PR 4), oder braucht es eine Migrations-Strategie?
2. Welche Claim-Typen müssen zwingend an Evidenz gekoppelt werden, welche nicht
   (z. B. reine Refactorings)?
3. Wie verhält sich der PR-Scope-Guard zu historischen Experimenten ohne
   maschinenlesbares Evidence-Pack?
