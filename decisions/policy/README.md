---
title: "Decisions/Policy (Stub-Namespace)"
status: active
canonicality: navigation
updated: "2026-05-18"
relations:
  - type: references
    target: ../../docs/foundations/repo-plan.md
---

# Decisions / Policy — Stub-Namespace

Dieser Namespace enthält aktuell nur dieses README als Stub-Marker; fachliche Artefakte liegen hier noch nicht.

`decisions/policy/` ist Teil der **typisierten Decision-Namespaces**
(`process/`, `system/`, `export/`, `policy/`, `benchmark/`), die im Repo-Plan
als Phase-C-Verstärker angelegt sind
(`docs/foundations/repo-plan.md` → „Typisierte Decision Artifacts").

**Zweck:** Hier landen Decision Artifacts, die Policy-Änderungen
(`docs/policies/*.md`) flankieren — Begründung, Geltungsbereich,
Stichtagsregelung, Rücknahmebedingung.

Bislang werden Policy-Änderungen direkt im jeweiligen Policy-Dokument
versioniert. Decisions würden hier nur entstehen, wenn eine Policy-Änderung
operativ tief greift (z. B. ein neues blockierendes Quality-Gate) und ein
separates Audit-Artefakt verlangt.

**Aktive Policy-Quellen:**

- `docs/policies/interpretation-budget.md`
- `docs/policies/pr-run-evidence-policy.md`
- `docs/policies/artifact-boundary-policy.md`
- `docs/policies/privacy-and-ethics.md`

**Schema:** Decision-Artifacts ohne `decisions/system/`-Bezug haben aktuell
**keinen** Pflicht-Contract. Erst beim ersten realen Eintrag wird entschieden,
ob ein eigener Schema-Strang sinnvoll ist.
