---
title: "Methode: System-Map Artifact Coupling Isolation"
status: draft
canonicality: operative
---

# method.md — System-Map Artifact Coupling Isolation

## Zielhypothesen

### H1 — Workflow-Hypothese
stale `system-map.md` ist primär workflowbedingt: Der Fehler entsteht, weil nach dem
Schreiben von Artifact-Dateien kein sofortiger canonical refresh erfolgt.

**Was H1 stützen würde:**
- Gegenlauf ohne Artifact-Write zeigt kein stale system-map (kein CI-Blocking-Fehler).
- Das Muster ist ausschließlich an `artifact_write_performed = true` geknüpft.
- `make generate` nach jedem Artifact-Write verhindert das Problem vollständig.

**Implikation wenn H1:** Das Problem ist lösbar durch Workflow-Disziplin. Kein
Architekturanteil. Keine Grenzänderung nötig.

### H2 — Boundary-/Architekturhypothese
stale `system-map.md` weist auf ein tieferes Koppelproblem hin: canonical diagnostics
(`system-map.md` via `git ls-files`) reagieren auf run-interne Artefakte, die nicht Teil
der eigentlichen fachlichen Änderung sind — unabhängig von der Reihenfolge.

**Was H2 stützen würde:**
- Stale system-map tritt auch ohne Artifact-Write auf (z.B. nach jeder Art von
  file-add in `experiments/`).
- Die Zähllogik via `git ls-files` hat keinen Scope-Filter: alle Dateien im Repository,
  inkl. Experiment-Artefakte, fließen in die system-map ein.
- Selbst korrekte Workflow-Reihenfolge lässt das Problem strukturell bestehen.

**Implikation wenn H2:** Das Problem erfordert eine Grenzentscheidung: Sollen
run-interne Artefakte Teil der canonical diagnostics sein oder nicht?

---

## Testfälle

### T-1: Gegenlauf ohne Artifact-Write (Haupttest)

**Ziel:** H1 vs. H2 trennen.

**Setup:**
- Sauberer Branch-Zustand auf `main`
- `make generate && make validate` = grün

**Änderung:**
- Eine kleine canonical-source-Änderung (1–3 Zeilen in einem bestehenden Dokument)
- Kein Schreiben neuer Dateien unter `artifacts/run-*/`
- `make generate` einmal ausführen
- `make validate` ausführen
- Commit + PR öffnen

**Beobachtung (zu erfassen in evidence.jsonl):**
- Tritt stale `system-map.md` im CI auf? Ja/Nein
- `artifact_write_performed`: false
- `ci_blocking_failures_total`: zu messen
- `changed_canonical_count`: zu messen
- `changed_derived_count`: zu messen
- `changed_ephemeral_count`: zu messen
- `trigger_point`: zu messen

**Interpretation:**
- Kein stale → stützt H1 (Workflow-Erklärung)
- stale trotzdem → stützt H2 (Boundary-Erklärung)

### T-2: Kontrollfall mit Artifact-Write (Replik des bekannten Musters)

**Ziel:** Bestätigung, dass das bekannte Muster im selben Setup reproduzierbar ist.

**Setup:** Identisch zu T-1, aber mit Schreiben mindestens einer Datei unter `artifacts/`.

**Beobachtung:**
- Erwartung: stale `system-map.md` wie in Run-003 bis Run-006
- Falls nicht auftritt: Muster weniger stabil als angenommen (relevant für Diagnose)

**Hinweis:** T-2 kann aus dem Predecessor-Experiment als belegt gelten
(Run-003 bis Run-006). Ein neuer T-2-Lauf ist optional.

---

## Explizite Trennung der Erklärungen

| Beobachtung                              | Stützt H1 | Stützt H2 | Mehrdeutig |
|------------------------------------------|-----------|-----------|------------|
| T-1: kein stale, kein Artifact-Write     | ✓         |           |            |
| T-1: stale auch ohne Artifact-Write      |           | ✓         |            |
| T-2: stale nach Artifact-Write (Replik)  | ✓ oder ✓  | ✓ oder ✓  | ✓ (allein nicht trennend) |
| Generator-Zähllogik ohne Scope-Filter    |           | ✓ (Anhaltspunkt) |       |
| `make generate` nach Write löst Problem  | ✓         |           |            |
| Problem persistiert nach korrektem Workflow |        | ✓         |            |

**Hinweis zu Mehrdeutigkeit:** T-2 allein (stale nach Artifact-Write) trennt nicht zwischen
H1 und H2, weil es beides erklären kann. Nur T-1 schafft die Trennung.

---

## Metriken (pro Lauf zu erheben oder als `not_measured` zu markieren)

| Metrik                         | T-1 | T-2 |
|-------------------------------|-----|-----|
| `artifact_write_performed`    | false | true |
| `changed_canonical_count`     | messen | messen |
| `changed_derived_count`       | messen | messen |
| `changed_ephemeral_count`     | messen | messen |
| `ci_blocking_failures_total`  | messen | messen |
| `manual_regen_steps`          | messen | messen |
| `diagnosis_clarity_score`     | messen | messen |
| `unnecessary_commit_delta`    | messen | messen |
| `trigger_point`               | messen | messen |
| `supports_workflow_hypothesis` | ableiten | ableiten |
| `supports_boundary_hypothesis` | ableiten | ableiten |

`supports_*` nur setzen wenn: direkt aus Beobachtung ableitbar und evidenzgetragen.
Keine freien Bewertungen.

---

## Keine stille Glättung

Wenn T-1 nur teilweise trennt (z.B. stale tritt in T-1 auf, aber aus einem anderen Grund
als erwartet), muss das explizit notiert werden. Keine scheinharte Ursachenbehauptung.

---

## Erfolgskriterien dieses Experiments

- **Mindestens:** T-1 ist definiert und durchführbar dokumentiert.
- **Ideal:** T-1 durchgeführt, Beobachtung eindeutig H1 oder H2 zuweisbar.
- **Akzeptabel:** T-1 durchgeführt, Ergebnis teilweise trennend; Restmehrdeutigkeit explizit.
- **Nicht akzeptabel:** Fake-Run, Pseudo-Ausführung, oder vorschnelle Ursachen-Behauptung
  ohne belegte Beobachtung.

---

## Risiken und Einschränkungen

- **Confounders:** Wenn T-1 einen anderen Branch-Zustand hat als T-2, könnte die
  Beobachtung durch Branch-Artefakte verzerrt sein → identischer Start-Zustand sicherstellen.
- **Scope-Drift:** T-1 darf keine neuen Artefakteordner anlegen — sonst ist das
  Experiment nicht sauber getrennt.
- **Partial evidence:** Predecessor-Experiment deckt T-2 bereits ab (Run-003 bis Run-006);
  aber Kontext-Gleichheit zu T-1 ist nicht vollständig gesichert.
- **Einzel-Run:** Auch ein sauberes T-1-Ergebnis ist nur ein Datenpunkt; breitere
  Replikation bleibt Aufgabe späterer Experimente.
