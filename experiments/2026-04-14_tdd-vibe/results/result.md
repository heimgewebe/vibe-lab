---
title: "TDD-Vibe — Ergebnisse"
status: testing
canonicality: operative
---

# result.md — Ergebnisse

## Messwerte im Vergleich

| Metrik                        | Implementation-First | TDD-Vibe              |
| ----------------------------- | -------------------- | --------------------- |
| HTTP-Status-Abdeckung (von 7) | 7/7                  | 7/7 (6/7 assertiert)  |
| Generierte Test-Cases         | 0                    | **41**                |
| Fehlerfall-Tests (4xx)        | 0                    | **22 (54 %)**         |
| Happy-Path-Tests              | 0                    | 19 (46 %)             |
| Implementierungszeilen        | 169                  | 249                   |
| Benötigte Prompts             | 1                    | 2                     |
| Testbarkeit (Store-Reset)     | Nicht vorhanden      | `_resetStore()` export |

## Beobachtungen

### Was TDD-Vibe besser macht

**Edge-Case-Abdeckung.** Der Test-First-Schritt zwang zur expliziten Formulierung von 22 Fehlerfall-Tests, bevor eine einzige Zeile Implementierung geschrieben wurde. Darunter Fälle, die im direkten Prompting nicht aufgetaucht wären:
- Case-insensitives Duplikat-Check (`IRIS@EXAMPLE.COM` vs. `iris@example.com`)
- E-Mail-Freigabe nach Löschung (kann danach neu registriert werden)
- Double-Delete → 404 (kein stilles Ignorieren)
- `createdAt` unveränderlich nach Update, `updatedAt` ändert sich

**Code-Design.** Durch den Test-Zwang entstanden sauberere Abstraktionen:
- Typisierte Envelopes (`SuccessEnvelope<T>`, `ErrorEnvelope`) statt `any`
- Extrahierte Helpers (`isEmailTaken`, `normaliseEmail`, `normaliseName`)
- `_resetStore()` für Testisolation — ein Designdetail, das impl-first nie brauchte

**Explizite Lücken.** Die fehlende 500-Behandlung ist in der Test-Suite direkt sichtbar und erweiterbar. Bei impl-first ist die Lücke unsichtbar.

### Was TDD-Vibe *nicht* automatisch löst

**500-Status-Abdeckung.** Beide Ansätze fehlen 500 (Internal Server Error). TDD-Vibe macht die Lücke sichtbarer (kein 500-Test → kein 500-Handling), löst sie aber nicht automatisch. Die Tests begrenzen die Implementierung auf das, was explizit getestet wurde.

**Mehraufwand.** 2 Prompts statt 1. Zudem mehr Implementierungszeilen (249 vs. 169) — nicht weil die Logik komplexer ist, sondern weil TDD-Vibe mehr explizite Typisierung und Extraktion erzwingt.

## Erkenntnisse

1. **TDD-Vibe verlagert Edge-Case-Arbeit nach vorne** — statt reaktiv (nach Bugbericht) werden Fehlerfälle proaktiv in Tests formuliert. Das ist der Kerngewinn.

2. **Tests als Spec sind präziser als Sprache** — "Duplikat-Check" in natürlicher Sprache ist vage. `expect(res.status).toBe(409)` nach IRIS-/iris-Test ist exakt. Die Präzision von Tests übertrifft die von Prosa-Specs.

3. **Test-First erzwingt besseres Design** (kleiner, aber messbarer Effekt): `_resetStore()`, typisierte Envelopes und extrahierte Helpers entstanden, weil Tests es erforderten.

4. **HTTP 500 ist in beiden Ansätzen vorhanden, aber ungetestet.** Der globale Error-Handler sitzt in `app.ts` (Express error-middleware). TDD-Vibe macht die fehlende Test-Abdeckung durch Abwesenheit sichtbar — kein Test löst einen unhandled-exception-Pfad aus. Das ist behebbar durch einen expliziten 500-Test-Case.

5. **Messbarkeit als Nebenprodukt** — TDD-Vibe-Rework ist messbar (Tests laufen oder nicht). Impl-First-Rework ist subjektiv.

## Entscheidung

→ Siehe `decision.yml` — Verdict: `iterate`

Hypothese **teilweise bestätigt**: TDD-Vibe liefert nachweislich mehr Edge-Case-Abdeckung und besseres Design. HTTP-Coverage ist technisch 7/7 in beiden Ansätzen (500-Handler in app.ts vorhanden), aber TDD-Vibe assertiert nur 6/7 direkt — was die Test-Lücke explizit sichtbar macht. Der nächste Iterationsschritt ist ein **Spec-First + TDD-Vibe Combo** — wo die Spec explizit Error-Klassen definiert, die dann als Test-Targets dienen.
