---
title: "Ergebnis: System-Map Artifact Coupling Isolation"
status: draft
canonicality: operative
relations:
  - type: informed_by
    target: "../../2026-04-19_generated-artifact-contract-validation/results/cross-run-assessment.md"
---

# result.md — Ergebnis

## Zusammenfassung

Dieses Experiment ist ein Diagnose- und Designexperiment. Es wurde kein echter
Testlauf durchgeführt. Die offene Leerstelle aus dem Predecessor-Experiment
`2026-04-19_generated-artifact-contract-validation` ist präzise übersetzt
worden, aber noch nicht empirisch geschlossen.

**Offene Ursachenfrage:**
Ist der wiederkehrende stale-`system-map.md`-Fehler primär ein Workflow-Artefakt
(Reihenfolge) oder ein Architektur-/Boundary-Problem (Kopplung als Designfrage)?

---

## Beobachtungen aus dem Predecessor (übertragen, nicht neu erhoben)

- stale `system-map.md` trat in Run-003 bis Run-006 nach Artifact-Write auf.
- Pro Run war ein zusätzlicher canonical-Regenerationscommit nötig.
- Generator-Zähllogik: `git ls-files` ohne Scope-Filter → alle Repo-Dateien
  fließen in die system-map, einschließlich run-interner Artefakte.
- Run-006 dokumentiert pre-artifact sauber, post-artifact stale: Trigger-Zeitpunkt
  ist unmittelbar nach Artifact-Write.

---

## Deutung (Vorläufig — kein eigener Run)

> Klare Trennung zwischen Beobachtung und Deutung. Folgendes ist Interpretation
> des Predecessor-Materials, nicht eigene Messung.

### Was spricht für Workflow-Hypothese (H1)?

- Trigger-Zeitpunkt konsistent: stale entsteht immer nach Artifact-Write.
- Behebung konsistent: `make generate` nach Artifact-Write löst das Problem.
- Vorabsauberkeit in Run-006 vor Artifact-Write deutet darauf hin, dass
  der Fehler nicht konstant vorhanden ist, sondern gezielt erzeugt wird.

### Was spricht für Boundary-/Architekturhypothese (H2)?

- `git ls-files` hat keinen Scope-Filter: run-interne Artefakte sind
  designbedingt Teil der canonical diagnostics.
- Das Problem würde auch bei konsequenter Workflow-Disziplin als Designfrage
  bestehen bleiben: Sollen Experiment-Artefakte die system-map-Zählung beeinflussen?
- Canonical-blocking auf run-interne Artefakte bedeutet: jede Run-Dokumentation
  muss einen zusätzlichen Regenerationsschritt auslösen — das ist keine reine
  Bedienungsfrage, sondern eine Architekturentscheidung.

### Was bleibt mehrdeutig?

- H1 und H2 schließen sich nicht vollständig aus. Auch wenn H1 zutrifft
  (Reihenfolge als Trigger), wäre H2 eine separate, legitime Folgefrage
  (Kopplung als Designentscheidung).
- Ohne T-1-Lauf (Gegenlauf ohne Artifact-Write) kann nicht belegt werden,
  ob das Problem ausschließlich an Artifact-Write hängt.
- Ein einzelner T-1-Lauf würde die Frage eingrenzen, aber nicht abschließend
  beantworten (Replizierbarkeit, Kontext-Kontrolle).

---

## Offene Restzweifel

1. **T-1 steht aus.** Die zentrale Beobachtung (stale ohne Artifact-Write? Ja/Nein)
   ist nicht erhoben.
2. **Keine identischen Kontrollbedingungen.** Predecessor-Runs hatten unterschiedliche
   Branch-Zustände; T-1 vs. T-2 unter identischen Startbedingungen ist noch nicht erfolgt.
3. **Generator-Implementierung könnte sich ändern.** Aktueller Befund gilt für den
   Stand des Generators zum Zeitpunkt des Designs.

---

## Keine Lösungsempfehlung

Dieses Experiment ist auf Diagnose beschränkt. Eine Lösungsempfehlung (Workflow-Regel,
Scope-Filter im Generator, o.ä.) steht nicht im Scope.

---

## Nächster Schritt (wenn weitergeführt)

T-1 durchführen: minimaler PR ohne Artifact-Write, CI-Ergebnis dokumentieren,
`artifact_write_performed = false` in evidence.jsonl festhalten,
`supports_workflow_hypothesis` / `supports_boundary_hypothesis` nur wenn direkt
aus Beobachtung ableitbar.
