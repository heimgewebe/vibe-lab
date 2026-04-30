---
title: "RRG-03 Remediation Strategy Comparison"
status: draft
canonicality: operative
created: "2026-04-30"
updated: "2026-04-30"
relations:
  - type: references
    target: "../../experiments/2026-04-23_agent-failure-surface/artifacts/run-phase-f-rrg03-real/observed.json"
  - type: references
    target: "../../experiments/2026-04-23_agent-failure-surface/results/phase-f-rrg03-locator-drift.md"
  - type: references
    target: "../../decisions/process/2026-04-30-rrg03-remediation-boundary.yml"
  - type: references
    target: "../../contracts/command-semantics.md"
---

# RRG-03 Remediation Strategy Comparison

## These / Antithese / Synthese

**These:** RRG-03 ist fixture-spezifisch belegt und das Patch-Gate ist ausgelöst.

**Antithese:** Der Beleg entscheidet nicht automatisch die technische Remediation.
Das Patch-Gate signalisiert Handlungsbedarf, nicht eine spezifische Lösung.

**Synthese:** v0.2 braucht einen Strategie-Vergleich vor jedem Schema-,
Validator- oder Runtime-Eingriff. Die Kandidaten müssen gegen denselben
Ist-Zustand bewertet werden, der den Befund erzeugt hat.

---

## Belegter Ist-Zustand

Quellen:
- `experiments/2026-04-23_agent-failure-surface/artifacts/run-phase-f-rrg03-real/observed.json`
- `experiments/2026-04-23_agent-failure-surface/results/phase-f-rrg03-locator-drift.md`
- `decisions/process/2026-04-30-rrg03-remediation-boundary.yml`

| Feld | Wert |
|------|------|
| classification | drifted |
| patch_gate.triggered | true |
| proof_scope | fixture_only |
| allgemeine Runner-Sicherheitsaussage | nicht belegt |
| allgemeine Locator-Sicherheitsaussage | nicht belegt |
| aktuelle Boundary | proposed, kein Patch |

Der Real-Run (Phase F) hat belegt: Nach realer Step-A-Mutation (C2) driftet
der Step-B-Locator `"Validate token"` von C1 Zeile 4 (byte 33–47) auf C3
Zeile 7 (byte 81–95). Der Beleg gilt ausschließlich für diese Fixture.

---

## Kandidatenmatrix

| # | Kandidat | Beschreibung |
|---|----------|--------------|
| 1 | **post_apply_anchor** | Nach jedem Apply-Schritt wird ein Anker (z.B. Zeilennummer + Hash-Snapshot) festgeschrieben, der als Ausgangspunkt für die nächste Resolution dient. |
| 2 | **byte_range** | Das Kommando enthält neben dem lesbaren Locator auch einen byte_start/byte_end-Anker, der nach Step A neu ausgewertet wird. |
| 3 | **exact_before hash / snapshot binding** | `exact_before` wird durch einen SHA256-Hash des Kontexts gebunden; Mismatch blockiert Step B sofort. |
| 4 | **explicit re_resolution_required** | Kommandokette deklariert explizit, dass nach jedem Apply eine erneute Resolution für Folgekommandos nötig ist. Verletzung = Fehler. |
| 5 | **validator warning for multi-match locator** | Validator warnt, wenn ein Locator innerhalb einer Chain mehr als einmal matcht und kein post_apply_anchor gesetzt ist. |
| 6 | **runner-side resolver hardening** | Runtime-Patch in `tools/vibe-cli/replay_minimal.py`: nach jedem Apply wird der Locator erneut aufgelöst und ein Drift-Check durchgeführt. |
| 7 | **no_patch_observe_more** | Keine semantische, validatorische oder Runtime-Änderung; weitere Real-Runs abwarten, bevor eine Remediation entschieden wird. |

---

## Bewertungskriterien

| Kriterium | Erläuterung |
|-----------|-------------|
| Adressiert Ursache? | Drift entsteht aus schwacher Folgeadressierung. Behebt der Kandidat das semantisch? |
| Maschinell prüfbar? | Kann die Invariante automatisch geprüft werden (Schema, Validator, CI)? |
| Rückwärtskompatibilität | Bricht der Kandidat bestehende Chains oder Fixtures? |
| Risiko falsch-positiver Signale | Kann der Kandidat Drift-Alarm auslösen, wo keiner vorliegt? |
| Scope-Drift | Weitet der Kandidat den Patch-Scope über fixture_only hinaus aus? |
| Aufwand | Relative Einschätzung des Implementierungsaufwands. |
| Verhältnis zu command-semantics v0.1 | Schärft der Kandidat die bestehende Semantik oder bricht er sie? |
| Benötigte Zusatzbelege | Welche weiteren Real-Runs oder Diagnosen sind Voraussetzung? |

### Kandidatenbewertung

| Kandidat | Ursache? | Maschinell? | Rückwärtskomp. | Falsch-positiv | Scope-Drift | Aufwand | v0.1-Verhältnis | Zusatzbelege |
|----------|----------|-------------|----------------|----------------|-------------|---------|-----------------|--------------|
| post_apply_anchor | ja | ja (Schema) | mittel | niedrig | niedrig | mittel | schärft | 1 Real-Run alt. Fixture |
| byte_range | teilweise | ja (Schema) | niedrig (breaking) | niedrig | niedrig | hoch | bricht | mehrere Fixtures |
| exact_before hash | teilweise | ja (Validator) | mittel | niedrig | niedrig | mittel | schärft | 1 Real-Run |
| re_resolution_required | ja | ja (Schema+Validator) | mittel | niedrig | niedrig | niedrig | schärft | 1 Real-Run |
| validator multi-match | nein (Symptom) | ja (Validator) | hoch | mittel | niedrig | niedrig | schärft | 1 Real-Run |
| runner hardening | nein (Symptom) | nein | hoch | mittel | hoch | hoch | außerhalb v0.1 | viele Fixtures, allg. Beleg |
| no_patch_observe_more | nein | nein | hoch | keines | keines | keines | neutral | weitere Real-Runs |

---

## Vorläufiges Ergebnis

**Kein finaler Gewinner.**

Wahrscheinlicher Leitkandidat: command-contract-first mit `post_apply_anchor`
oder `re_resolution_required` als zu prüfende Hypothese. Beide adressieren
die Ursache (schwache Folgeadressierung) semantisch und sind maschinell
prüfbar, ohne den Patch-Scope über den belegten Fixture-Befund hinaus
auszuweiten.

`runner-side resolver hardening` und `validator warning for multi-match locator`
bleiben deferred: Sie adressieren Symptome, nicht die Ursache, und benötigen
einen allgemeineren Beleg, den der aktuelle Real-Run (fixture_only) nicht
liefert.

`no_patch_observe_more` bleibt zulässig und ist mit allen anderen Kandidaten
kombinierbar.

**Kein accepted decision status** — dieser Vergleich ist Grundlage für ein
Decision Preimage, nicht für eine abgeschlossene Entscheidung.

---

## Erforderliche nächste Belege

1. Mindestens ein zusätzlicher Real-Run für RRG-03 mit alternativer Fixture
   (anderer Locator, anderes Dokument, anderes Drift-Muster).
2. Separate Diagnose, ob RRG-01 und RRG-02 denselben Remediation-Pfad
   benötigen oder ob ihre Drift-Ursachen abweichen.
3. Prüfung, ob v0.2 einen Breaking Change für bestehende Chains bedeutet —
   insbesondere bei `byte_range` und `re_resolution_required`.
4. Erst danach: Decision Preimage auf Basis dieses Strategie-Vergleichs und
   der zusätzlichen Belege.

---

## Nicht-Ziele dieses Dokuments

- Keine Runtime-/Schema-/Validator-/CI-Änderung.
- Keine Aufwertung von
  `decisions/process/2026-04-30-rrg03-remediation-boundary.yml`
  von `proposed` auf `accepted`.
- Keine v0.2-Implementierung.
- Kein neuer CI-Gate.
