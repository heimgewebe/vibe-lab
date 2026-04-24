---
title: "Ergebnisse: Phase 1b — Validator Classification Sharpness"
status: draft
canonicality: operative
created: "2026-04-24"
updated: "2026-04-24"
author: "GPT-5.3-Codex"
relations:
  - type: references
    target: evidence.jsonl
  - type: references
    target: decision.yml
  - type: references
    target: ../artifacts/run-2026-04-24-phase1b-001/execution.txt
  - type: references
    target: ../artifacts/run-2026-04-24-phase1b-001/run_meta.json
---

# Ergebnisse: Phase 1b — Validator Classification Sharpness

## Hypothese (Reprise)

> Die Ablehnungs-Korrektheit des agent_handoff-Validators ist für Phase-1-Driftfälle gegeben,
> aber die Fehlerklassifikation bleibt für Locator-/Target-Drift unscharf;
> ein Layer-Vergleich mit cross_contract macht die Zustandsgrenze explizit.

**Verdict: Bestätigt.**

---

## Ausführung

- **Run-ID:** `run-2026-04-24-phase1b-001`
- **Branch:** `experiments/phase-1b-classification-sharpness-execution`
- **Executor:** `local:developer`
- **Artefakte:** `artifacts/run-2026-04-24-phase1b-001/`

---

## Befund 1: Ablehnungs-Korrektheit (agent_handoff, strict mode)

Alle 6 Phase-1-Driftfälle korrekt abgelehnt (exit 1):

| Fall | Drift-Typ | Emittierter Label | Korrekt abgelehnt |
|------|-----------|-------------------|-------------------|
| A1 | locator_drift (ungültiger Pfad) | `hash_mismatch` | ✅ |
| A2 | locator_drift (Fragment-Probe) | `hash_mismatch` | ✅ |
| B1 | hash vollständig geändert | `hash_mismatch` | ✅ |
| B2 | hash Ein-Nibble-Drift | `hash_mismatch` | ✅ |
| C1 | target_files drift | `hash_mismatch` | ✅ |
| D1 | change_type structural (rename) | `contract_invalid` | ✅ |

**Ablehnungs-Korrektheit: 6/6 = 100 % — vollständig bestätigt.**

---

## Befund 2: Klassifikationsschärfe (agent_handoff)

A1, A2, B1, B2, C1 erhalten alle denselben Label `hash_mismatch`.
Der Validator kann aus dem Hash-Mismatch allein nicht unterscheiden:

- ob der Locator verändert wurde (A1, A2)
- ob die Zieldatei(en) verändert wurden (C1)
- ob der Commit-Hash direkt manipuliert wurde (B1, B2)

**D1 ist der einzige Fall mit spezifischem Label** (`contract_invalid`), weil die Ursache im JSON-Schema-Constraint liegt (enum-Verletzung), nicht im Hash.

Klassifikationsschärfe für Locator-/Target-Drift: **unscharf** (Hash-Kompressions-Effekt).

Dies ist ein struktureller Befund, kein Fehler: `hash_mismatch` ist technisch korrekt und
intentional (der Hash sichert den Gesamtzustand). Die Schärfe-Lücke liegt in der fehlenden
Semantik des Rejection-Grunds.

---

## Befund 3: Klassifikationsschärfe (cross_contract)

Die cross_contract-Tests (`python3 -m unittest tests/contracts/test_cross_contract_chain.py`,
14/14 bestanden) zeigen:

| Test | Drift-Typ | Detektiert als | Status |
|------|-----------|----------------|--------|
| test_locator_drift_fails | Locator-Abweichung (Handoff vs. Chain) | `handoff_locator_drift` | ✅ |
| test_target_drift_fails | Target-Datei-Abweichung | eigene Klasse | ✅ |
| test_target_drift_extra_fails | Extra-Target im Chain | eigene Klasse | ✅ |
| test_state_drift_fails | State-Drift (exact_before/exact_after) | eigene Klasse | ✅ |

**cross_contract kann Locator-Drift, Target-Drift und State-Drift als separate Klassen
typisieren — agent_handoff komprimiert diese auf hash_mismatch.**

---

## Zustandsgrenze (Layer-Vergleich)

```
Drift-Typ         | agent_handoff (strict) | cross_contract
------------------|------------------------|----------------
locator_drift     | hash_mismatch          | handoff_locator_drift
target_drift      | hash_mismatch          | eigene Klasse
content_mutation  | hash_mismatch          | —
structural        | contract_invalid       | contract_invalid
```

Die beiden Layer sind **komplementär, nicht austauschbar:**
- agent_handoff: Integritäts-Prüfschicht (hash-basiert, schnell, zuverlässig)
- cross_contract: Semantische Drift-Typisierungs-Schicht (strukturell, klassen-ausdrucksstärker)

---

## Schlussfolgerungen

1. **Hypothese bestätigt.** Die Ablehnungs-Korrektheit ist vollständig (6/6). Die Klassifikations-
   schärfe ist für Locator-/Target-Drift strukturell begrenzt (hash_mismatch als Kompression).

2. **Kein Fehler, kein Handlungsbedarf in Phase 1.** Das Verhalten des agent_handoff-Validators
   ist korrekt für seinen Zweck (Integritätsprüfung). Eine Schärfung wäre eine explizite
   Funktionserweiterung — nicht in Phase 1 oder Phase 1b vorgesehen.

3. **Cross_contract als zweite Diagnoseebene.** Wer Drift-Typ-Klassen für Debugging oder
   Auditierung braucht, findet sie im cross_contract-Layer. Beide Layer zusammen ergeben ein
   vollständiges Bild.

4. **Informations-Verlust-Achse (dokumentiert in method.md):** Der Hash-Mismatch-Label ist
   informationsärmer als der Drift-Typ, den er repräsentiert. Dies ist eine bewusste Entscheidung
   des Validator-Designs (Kompression), nicht eine Lücke.

---

## Nächste Schritte

- Kein weiterer Handlungsbedarf für Phase 1b.
- Wenn eine schärfere Klassifikation im agent_handoff-Validator gewünscht ist:
  → Neues Experiment als Phase 1c (Validator-Erweiterung), nicht hier.
- Phase 2 beginnt unabhängig davon (kein Blocker durch Phase 1b-Befunde).
