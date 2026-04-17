---
title: "Experimenten-Labor (Index)"
status: active
canonicality: navigation
---

# 🔬 Experimenten-Labor

Dies ist das operative Labor des Vibe-Labs. Hier werden Hypothesen getestet und evaluierte Techniken auf ihre Robustheit geprüft.

## Abgeschlossene Vorstudien
- [Spec-First Prompting](2026-04-08_spec-first/CONTEXT.md)
- [YOLO vs Spec-First](2026-04-11_yolo-vs-spec-first/CONTEXT.md)
- [Spec-First Legacy Refactoring](2026-04-12_spec-first-legacy/CONTEXT.md)
- [TDD Vibe](2026-04-14_tdd-vibe/CONTEXT.md)

## Vergleichende Anschlussanalysen
- [Upfront Structuring Comparison](2026-04-14_upfront-structuring/CONTEXT.md)
- [Upfront Structuring Replication](2026-04-14_upfront-structuring-replication/CONTEXT.md)
- [Prompt-Length Control](2026-04-14_prompt-length-control/CONTEXT.md)

---

## Iteration und Ausführung

`iteration` und `execution_status` sind voneinander unabhängig:

- **iteration** ist die aktuell vorbereitete Iterationsstufe des Experiments. Sie kann erhöht werden, ohne dass eine Ausführung stattfindet.
- **execution_status** beschreibt den tatsächlichen Durchführungsgrad. Er bezieht sich auf evidenzgetragene Runs, nicht auf Planungsfortschritte.
- Die aktuelle Iteration kann `prepared` sein — das bedeutet, dass die Struktur bereit ist, aber keine Ausführung stattgefunden hat.

→ Vollständige Definition: [Experiment-Ontologie](../docs/concepts/experiment-ontology.md)

## Reconciliation

Experimente dürfen korrigiert werden, wenn ihr dokumentierter Zustand nicht mehr dem tatsächlichen Zustand entspricht. Dabei gilt:

- **Korrektur ≠ neue Ausführung.** Reconciliation bringt Manifest, Decision und Ergebnisse mit der tatsächlichen Evidenzlage in Einklang.
- **Dokumentation ist Pflicht.** Jede Reconciliation muss in der PR-Beschreibung als solche deklariert werden (PR-Typ: `experiment_reconciliation`).
- **Keine epistemische Aufwertung.** Reconciliation darf den Status, das Evidence-Level oder die Adoption-Basis nicht erhöhen.

→ Operativer Ablauf: [Playbook: Reconciliation](../docs/playbooks/reconciliation.md)
