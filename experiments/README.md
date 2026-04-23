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

## In Design (noch nicht ausgeführt)
- [Agent Failure Surface Mapping](2026-04-23_agent-failure-surface/CONTEXT.md) —
  fünfphasige Reihe zur adversarialen Härtung des Agent-Operability-Layers
  (Drift Injection, Semantic Contradiction, Chain Integrity Stress,
  Replay Reality Gap, Adversarial Agent Simulation). `status: designed`,
  jede Phase operativ gekoppelt an Fixture/Test/Validator-Konsequenz.

---

## Iteration und Ausführung

`iteration` und `execution_status` sind im aktuellen Repo nicht immer selbsterklärend.
Für Grenzfälle gilt die ergänzende Begriffsklärung in
[`docs/concepts/experiment-ontology.md`](../docs/concepts/experiment-ontology.md).

Kurzfassung:

- **iteration** zählt die Iterationsstufen des Experiments und kann erhöht werden,
  ohne dass eine Ausführung stattgefunden hat.
- **execution_status** beschreibt den tatsächlichen Durchführungsgrad. Er bezieht
  sich auf evidenzgetragene Runs, nicht auf Planungsfortschritte.
- Wenn `iteration` erhöht wurde, aber noch kein neuer Run vorliegt, muss der
  dokumentierte Ausführungsstand dies klar widerspiegeln.

## Reconciliation

Experimente dürfen korrigiert werden, wenn ihr dokumentierter Zustand nicht mehr dem tatsächlichen Zustand entspricht. Dabei gilt:

- **Korrektur ≠ neue Ausführung.** Reconciliation bringt Manifest, Decision und Ergebnisse mit der tatsächlichen Evidenzlage in Einklang.
- **Dokumentation ist Pflicht.** Jede Reconciliation muss in der PR-Beschreibung als solche deklariert werden (PR-Typ: `experiment_reconciliation`).
- **Keine epistemische Aufwertung.** Reconciliation darf den Status, das Evidence-Level oder die Adoption-Basis nicht erhöhen.

→ Operativer Ablauf: [Playbook: Reconciliation](../docs/playbooks/reconciliation.md)
