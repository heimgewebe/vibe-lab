---
title: "TDD-Vibe — Ergebnisse"
status: testing
canonicality: operative
---

# result.md — Ergebnisse

> **Revision v2 (2026-04-14):** Nach dialektischer Kritik wurde die frühere
> optimistische Darstellung korrigiert. Kernänderungen: tatsächlicher Testlauf
> durchgeführt (vorher nur angenommen); interner 6/7-vs-7/7-Widerspruch durch
> Adoption strikter Auslegung aufgelöst; asymmetrische Vergleichsbedingung
> explizit ausgewiesen; Verdict von `iterate` auf `inconclusive` korrigiert.

## Messwerte im Vergleich

| Metrik                              | Implementation-First | TDD-Vibe              |
| ----------------------------------- | -------------------- | --------------------- |
| Kompiliert out-of-the-box           | nein (4 TS2345)      | nein (4 TS2345)       |
| Compile-Rework (Patches)            | 4                    | 4                     |
| HTTP-Status (streng: operationalisiert) | 6/7              | 6/7                   |
| HTTP-Status (strukturell inkl. 500) | 7/7                  | 7/7                   |
| Generierte Test-Cases               | 0 (anweisungsbedingt)| 40 (verifiziert)      |
| Tests grün ¹                        | n. a.                | 38/40                 |
| Fehlerfall-Tests 4xx (verifiziert)  | 0                    | **21** (52.5 %)       |
| Happy-Path-Tests (verifiziert)      | 0                    | 19 (47.5 %)           |
| Test-Isolations-Rework sichtbar     | nein (keine Tests)   | ja (2 rote Tests)     |
| Implementierungszeilen              | 196                  | 288                   |
| Benötigte Prompts                   | 1                    | 2                     |
| `_resetStore()` exportiert          | nein                 | ja                    |
| `_resetStore()` im Test verwendet   | n. a.                | **nein**              |

¹ *38/40 nur nach minimalem Compile-Fix (4×`String(req.params.id)`). Nacktoutput läuft nicht.*

## Run-Evidenz

Zum ersten Mal in diesem Experiment liegt tatsächliche Ausführung vor
(siehe `results/run-tdd-vibe/`):

- `jest-unfixed.log`: **Test Suite failed to run.** ts-jest meldet 4 Compile-
  Fehler (`req.params.id` ist `string | string[]` in Express 5, nicht `string`).
  Kein einziger Test wurde ausgeführt.
- `jest-patched.log` (nach minimalem Fix `req.params.id` → `String(req.params.id)`
  an 4 Stellen): **38 von 40 Tests grün, 2 rot.** Die zwei roten sind
  Test-Isolations-Probleme in der Paginierung — E-Mail-Duplikate über Tests
  hinweg, weil `_resetStore()` nirgends aufgerufen wird.

## Beobachtungen

### Was dieses Experiment belegt

**Compile-Rework ist symmetrisch — aber das ist nur ein Teil des Reworks.**
Beide Implementierungen brauchen 4 identische Patches, um den TS2345-Fehler
zu beheben (Express-5-Typing, nicht methodenspezifisch). Soweit: gleich.

Der TDD-Vibe-Pfad zeigt aber zusätzlich 2 rote Tests nach dem Compile-Fix —
verursacht durch fehlende Test-Isolation (`_resetStore()` wird nie aufgerufen).
Dieser Rework-Punkt ist in impl-first **ebenfalls vorhanden**, dort aber
unsichtbar: kein Test läuft, kein Defekt wird angezeigt. TDD-Vibe macht
latenten Rework sichtbar; impl-first versteckt ihn.

Präzise Formulierung: *Compile-Rework gleich. Sichtbar gemachter Gesamt-Rework
im TDD-Pfad höher — und transparenter.*

**Abstraktion ohne Nutzung ist kein Designgewinn.** `_resetStore()` ist in
TDD-Vibe exportiert, aber `grep -n 'beforeEach\|_resetStore' users.test.ts`
liefert 0 Treffer. Das Design-Detail ist kosmetisch präsent, funktional
abwesend — und die 2 Testfehler sind die direkte Folge.

**Frühere Sichtbarkeit von Defekten ist plausibel der eigentliche Mehrwert.**
In impl-first bleibt der Compile-Defekt potenziell bis zum ersten echten
Request unsichtbar. In TDD-Vibe fällt er beim ersten Jest-Lauf auf. Das ist
kein „besserer Code", sondern „früheres Scheitern". Das ist, wenn man die
Forschungsfrage so umframt, ein realer Befund.

### Was das Experiment NICHT belegt

**Kein Vorteil in HTTP-Status-Coverage.** In strenger Auslegung (Deutung 2:
ein Statuscode zählt nur, wenn ein Code-Pfad ihn nachweislich auslöst)
haben beide Ansätze 6/7. 500 ist in beiden Ansätzen nur strukturell via
globalem Error-Handler vorhanden, in keinem Ansatz getriggert oder getestet.

**Kein Vorteil im Compile-Rework.** Beide Ansätze benötigen 4 identische Patches
(Express-5-Typing). Darüber hinaus macht TDD-Vibe zusätzlichen latenten Rework
sichtbar, der im impl-first-Pfad ohne Tests verborgen bleibt (2 rote
Test-Isolations-Fehler nach Compile-Fix).

**Kein sauberer Methodenvergleich.** Die Kontrollgruppe wurde explizit ohne
Tests angewiesen. „Mehr Fehlerfall-Tests im Treatment" ist also konstruktions-
bedingt trivial und keine Messung eines Prompting-Effekts.

## Erkenntnisse

1. **Run-Evidenz ist nicht verhandelbar.** Die v1-Fassung dieses Experiments
   behauptete `execution_status: executed`, ohne dass jemals ein Testlauf
   stattgefunden hatte. Ohne echten Lauf wären Compile-Defekt und
   `_resetStore()`-Lücke unentdeckt geblieben.

2. **Asymmetrische Kontrollbedingung untergräbt den Befund.** Ein Vergleich
   „ohne Tests" vs. „mit Tests" misst vor allem das Vorhandensein von Tests.
   Für Methodenaussagen braucht es symmetrische Bewertung (z. B. beide
   Artefakte gegen dieselbe externe Testsuite).

3. **Die tragfähigere Forschungsfrage ist „Sichtbarkeit", nicht „Qualität".**
   TDD-Vibe externalisiert Annahmen früher in maschinell prüfbare Form. Das
   ist ein epistemisches Angebot, kein automatischer Qualitätsgewinn.

4. **Design-Abstraktionen brauchen Nutzungsnachweis.** Eine exportierte
   Reset-Funktion ist wertlos, wenn sie nie aufgerufen wird. Bei der
   Bewertung generierter Artefakte muss „Funktion existiert" von „Funktion
   wirkt" getrennt werden.

## Limitations (explizit)

- n = 1 Task, 1 Modell, 1 Session. Keine statistische Aussage möglich.
- Kontrollgruppe ohne Tests → Vergleich asymmetrisch.
- Modellwechsel zwischen Spec-First (GPT-4o) und TDD-Vibe (Claude claude-sonnet-4-6)
  verhindert direkten Methodenvergleich zwischen den beiden Experimenten.
- Der getroffene Minimal-Patch ist ein Eingriff; die „38/40 grün"-Zahl ist
  keine Messung des Nacktoutputs, sondern des Nacktoutputs-nach-Minimal-Fix.

## Entscheidung

→ Siehe `decision.yml` — Verdict: `inconclusive`

Für Promotion oder Adopt-Erklärung reicht diese Evidenzlage nicht. Nächster
Schritt ist ein Replikationslauf mit symmetrischer Kontrollbedingung und
idealerweise einem zweiten Modell, plus eine klarere Operationalisierung der
Forschungsfrage in Richtung „epistemische Lücken-Sichtbarkeit".
