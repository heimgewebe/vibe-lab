---
title: "Kontext: Pre-Mortem Prompting"
status: testing
canonicality: operative
---

# CONTEXT.md — Experiment-Kontext

## Ausgangslage

Dieses Experiment prüft, ob Pre-Mortem-Prompting Fehlpfadabdeckung verbessert und ob ein Failure-Learning-Loop über Sessions hinweg stabil bleibt.

## Run-Topologie

- Holdout: `run-007` vs. `run-008`
- Injection: `run-009` vs. `run-010`
- Failure-Learning: `run-011` → `run-012`
- Session-B-Replikation + Exotic Injection: `run-013` und `run-014`
- Extended-Pre-Mortem: `run-015`

## Repo-Validierungsstatus

`make validate` ist in dieser Umgebung weiterhin **nicht bestätigt**.
Installationsversuche für `pyyaml` via `pip` und `apt` sind an Proxy-403 gescheitert.

## Traceability

- **triggered_by:** User-Anfrage + Follow-up zu Replikation/Unknowns/Blindspots.
- **policy:** AGENTS.md / agent-policy.yaml
- **action:** Run-015 ergänzt, failure_modes erweitert.
- **outcome:** micro_price-Blindspot geschlossen; Validierungsumgebung weiterhin blockiert.
