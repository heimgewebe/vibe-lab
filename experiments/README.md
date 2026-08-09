---
title: "Experimenten-Labor (Index)"
status: active
canonicality: navigation
updated: "2026-08-08"
triggered_by: "bureau-task-OPERATOR-ECOSYSTEM-REDUNDANCY-V1-T005"
---

# 🔬 Experimenten-Labor

## Consumer- und Ablauf-Gate für neue Experimente

Jeder neue Experimentordner benötigt `registration.v2.json` nach `schemas/experiment.registration.v2.schema.json`. Eine Rückdatierung des Ordnernamens umgeht das Gate nicht; nur die beim T005-Preimage bereits vorhandenen Experimente besitzen eine geschlossene Kompatibilitätsausnahme.

Die Registrierung bindet das Experiment an:

- einen bestätigten, bis zum Ablauf aktuellen externen Consumer mit referenzierter Commitment-Grundlage;
- ein extern referenziertes Entscheidungsziel und numerische Erfolgs- sowie Schadens-/Falsifikationsschwellen;
- einen zum `registered_at`-Zeitpunkt zukünftigen Reviewtermin, Ablauf und eine eindeutige reviewed Zuordnung von Ergebniszuständen zu `promote`, `pilot`, `defer`, `reject` oder `archive`;
- einen bilanzierten Durable-Surface-Budget-Nachweis (eine Einheit je eindeutiger `add:`-/`remove:`-/`replace:`-/`retire:`-Referenz) oder eine extern überprüfte Ausnahme;
- eine explizite Grenze gegen automatische Policy-, Routing-, Queue-, Merge- und Runtime-Autorität.

Für `higher_is_better` gilt Erfolg inklusiv ab der Erfolgsschwelle und Schaden/Falsifikation bis zur Gegenschwelle; für `lower_is_better` umgekehrt. Ohne diese Angaben blockiert CI. Die Outcome-Zuordnung dokumentiert den vorgeschriebenen reviewed Abschluss; sie führt keine externe Änderung aus. Historische Registrierungen werden nicht nachträglich mit Consumer-, Evidenz- oder Reviewbehauptungen angereichert und erhalten aus der Kompatibilitätsausnahme keine neue Gültigkeit oder Autorität.


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
