---
title: "TDD-Vibe — Follow-Ups"
status: testing
canonicality: operative
---

# followups.md — Getrennt geführte Folgepfade

> Bewusst **nicht** in dieser PR umgesetzt. Diese Einträge beschreiben
> Eingriffe, die die Original-LLM-Artefakte (`artifacts/tdd-vibe/*`) verändern
> würden — genau die Artefakte, die aktuell Gegenstand der Evidenz sind. Ein
> stilles „Reparieren" würde die Nacktoutput-Messung rückwirkend falsifizieren.
>
> Wenn sie angefasst werden, dann als eigener Experiment-Iterationsschritt
> (iteration 2) mit dokumentierter Motivation und separater Evidenz-Spur,
> nicht als Wartungs-Commit.

## B1 — `_resetStore()` wirklich aufrufen (Test-Isolation)

**Problem.** `artifacts/tdd-vibe/users.ts` exportiert `_resetStore()`, aber
`artifacts/tdd-vibe/users.test.ts` ruft es nirgendwo auf. Die 2 roten
Paginierungs-Tests in `run-tdd-vibe/jest-patched.log` sind direkte Folge.

**Möglicher Eingriff.** In der Test-Datei einfügen:

```ts
import { _resetStore } from "./users";
beforeEach(() => _resetStore());
```

Alternativ: Jest so konfigurieren, dass das Modul pro Test neu geladen wird
(`jest.isolateModules` + `jest.resetModules`) — invasiver, aber ohne Touch
am Production-Code.

**Warum nicht jetzt.** Der Defekt ist selbst das Evidenzstück: er zeigt, dass
generierte Design-Abstraktionen ohne Nutzungsnachweis wertlos sind. Ein
stiller Fix würde Erkenntnis Nr. 4 aus `results/result.md` entkräften.

**Wie als Folgepfad.** Neues Experiment `2026-04-NN_tdd-vibe-iter2` oder
iteration:2 im selben Manifest, mit expliziter Hypothese „Integration des
Reset-Hooks behebt die 2 roten Tests ohne Seiteneffekte". Dann Original-
Artefakte neu generieren ODER expliziten Patch-Pfad führen.

## B2 — PUT /users/:id Body-Robustheit (`"name" in body`)

**Problem.** Der PUT-Handler prüft Felder mit `"name" in req.body`. Ist der
Body kein Object (z. B. `null`, `"string"`, `42`), wirft das einen Runtime-
TypeError und wird vom 500-Handler gefangen — fachlich wäre 400 oder 422 der
richtige Code. Aktuell nicht durch Tests abgedeckt, also latent.

**Möglicher Eingriff.** Guard vor den `in`-Checks:

```ts
if (typeof req.body !== "object" || req.body === null || Array.isArray(req.body)) {
  return res.status(422).json({ success: false, error: { message: "body must be an object" } });
}
```

**Warum nicht jetzt.** Der Defekt ist nicht Teil der dokumentierten
Rework-Messung. Ihn zu patchen hieße, die Zeile „Implementierungszeilen: 288"
rückwirkend zu verändern und den Nacktoutput zu schönen. Zudem: kein
bestehender Test deckt diesen Pfad ab — ein Fix ohne neuen Test wäre blind.

**Wie als Folgepfad.** Zuerst Test schreiben (`PUT /users/:id mit body=null
erwartet 422`), dann Fix. Damit wird B2 zum kleinen TDD-Replikationslauf,
der zusätzlich dokumentieren kann, ob das Modell den Fall beim zweiten
Versuch selbst fängt.

## B3 — Modell-symmetrische Replikation (operativer Mini-Spec)

**Ziel.** Prüfen, ob der beobachtete Unterschied zwischen TDD-Vibe und
Vergleichspfad bestehen bleibt, wenn beide Läufe mit identischem Modell unter
identischen Randbedingungen durchgeführt werden.

**Scope.** Ein eng begrenzter Replikationslauf im Labor-Kontext, ohne Promotion,
ohne Manifest-/Decision-Änderung und ohne Rückumschreiben bestehender Artefakte.

**Feste Vergleichsbedingungen (konstant halten).**

- gleiches Modell
- gleiche Aufgabe
- gleiche Tool-/Testumgebung
- gleiche Ausgabekriterien und Erfolgsmetriken

**Variieren.**

- ausschließlich Prompt-/Arbeitsmodus (`tdd-vibe` vs. Vergleichspfad)

**Erfolgskriterium (messbar).**

- Vergleich der Ergebnisdifferenz zwischen beiden Modi anhand derselben Metriken
  (mindestens: Teststatus, Rework-Umfang, Defektklassen)
- Erfolg bedeutet hier: replizierbare und nachvollziehbare Differenz unter den
  konstanten Bedingungen, nicht ein vorab festgelegter Sieger

**Interpretationsgrenze (nicht behaupten).**

- keine allgemeine Aussage, dass TDD-Vibe grundsätzlich überlegen ist
- nur Aussage für die konkret replizierte Konstellation (Aufgabe, Modell,
  Umgebung, Zeitpunkt)

**Traceability.**

- triggered_by: "Agenten-Pilotauftrag: eng begrenzte Operability auf
  2026-04-14_tdd-vibe/followups.md"
- policy: "AGENTS.md + agent-policy.yaml (Lab-Zone, minimal-lokale Änderung,
  keine Promotion, keine Governance-Änderung)"
- action: "Add B3 operational follow-up block for model-symmetric replication"
- outcome: "Replikationspfad ist präzise operationalisiert, ohne bestehende
  Evidenzartefakte umzuschreiben"

## Nicht-Ziele dieser Datei

- Keine Terminverpflichtung. Follow-Ups sind offen, nicht eingeplant.
- Keine impliziten Verbesserungen am Original-Artefakt. Wer diese Datei liest
  und daraus einen Fix schnitzt, schreibt einen eigenen Experiment-Eintrag.
