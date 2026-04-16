---
title: "Incremental vs. Single-Shot: Debuggability — Ergebnis"
status: testing
canonicality: operative
document_role: experiment
---

# result.md — Experiment-Ergebnis

**Verdict: inconclusive** | Confidence: low | Datum: 2026-04-14

## Zusammenfassung

Das Experiment wurde vollständig ausgeführt. Der Sonderfall "bugfreie Kontrolle" ist
eingetreten: Single-Shot produzierte auf allen 5 Inputs korrekte Ausgabe; der Incremental-Arm
(mit reintroduziertem doppelten i++-Bug in cli.ts) zeigte auf Input 3 und 4 sichtbare
Fehler, auf Input 5 einen latenten (unsichtbaren) Fehler.

Die primäre Hypothese — Incremental erlaubt frühere Lokalisierung (`first_failing_input_index`)
oder schnellere Behebung (`time_to_fix`) — konnte nicht direkt geprüft werden, weil ein
Arm bug-frei war und der andere vorsätzlich präpariert. Dieser Sonderfall war vorhersehbar
und wurde in den Erfolgskriterien nicht als Ausnahme geregelt.

## Beobachtungen

### Wirksamkeit (Bug-Detection)

| Metrik                        | Single-Shot | Incremental (buggy) | Δ / Bemerkung               |
| ----------------------------- | ----------- | ------------------- | --------------------------- |
| `first_failing_input_index`   | undefined   | 3                   | Nicht vergleichbar (SS 0 Bugs) |
| `time_to_fix_unguided`        | 0           | 1 Iteration         | SS hatte nichts zu fixen     |
| `time_to_fix_guided`          | 0           | 1 Iteration         | SS hatte nichts zu fixen     |
| `hidden_bugs_count`           | 0           | 3 (2+1 latent)      | Incremental: compiletransparente Bugs |
| `patch_size`                  | N/A         | 7 Zeilen, 1 Datei   | Lokalisiert auf cli.ts       |
| `correct_outputs (5 Inputs)`  | 5/5         | 2/5 sichtbar korrekt | Input 5 latent fehlerhaft    |
| `compilation_errors`          | 0           | 0                   | Bug compiletransparent in BEIDEN |

### Fehlerverhalten im Detail

**Single-Shot (index.ts, 227 Zeilen):**
- Input 1–5: alle korrekt, Exit 0
- Keine Laufzeitbugs; CLI-Argument-Parsing in eigenem switch-Block innerhalb `parseArgs()`

**Incremental (cli.ts + 6 weitere Dateien, ~170 Zeilen cli.ts):**
- Input 1: ✅ Korrekt — positional arg, kein Flag-Wert-Pair, Bug nicht getriggert
- Input 2: ✅ Korrekt — `--transform` ist letztes Flag, übersprungener Arg existiert nicht
- Input 3: ❌ FAIL — `--input file --format json`: `--input` überspringt `--format` durch doppeltes i++; `json` als positional arg ignoriert; Format bleibt CSV
- Input 4: ❌ FAIL — `--input file --format json --columns name,score`: `--format` übersprungen, `--columns` zufällig getroffen; CSV statt JSON mit Spaltenfilter
- Input 5: ⚠️ LATENT — `--filter department=Engineering --transform salary:uppercase`: `--filter` überspringt `--transform`; Zahlen-uppercase hat no-op-Effekt; Bug unsichtbar

**Bug-Mechanismus:** `requireNextArg()` liest den Wert korrekt; dann `i++` (korrekt, überspringt den Wert) + zweites `i++` (BUG, überspringt das nächste Flag). Der For-Loop-`i++` addiert noch einmal → insgesamt 3 Schritte statt 2 pro Flag-Wert-Pair.

### Modulare Fix-Barkeit

Der Fix war auf **eine Datei (cli.ts), 7 Zeilen** lokalisiert. Das entspricht der
Erwartung aus dem Design: Incremental-Arm kapselt CLI-Parsing vollständig in `cli.ts`.

Für einen äquivalenten Bug im Single-Shot-Arm wäre die betroffene Funktion `parseArgs()`
in `index.ts` (227 Zeilen). Die Fix-Größe wäre identisch (7 Zeilen). Kein messbarer
Patch-Größen-Vorteil durch Modularisierung.

Der potenzielle Vorteil der Modularisierung liegt im **Suchraum**: 7 Dateien im Incremental-Arm
vs. 1 Datei im Single-Shot. Beim Guided Fix ist dieser Unterschied irrelevant. Beim Unguided
Fix hätte ein Mensch durch mehr Dateien gesucht — aber ein erfahrener Entwickler findet
CLI-Parsing schnell durch Funktionsname (`parseAndValidateArgs`) oder Dateiname (`cli.ts`).

## Deutung

### Was messbar belegt ist

1. **Compiletransparenz des Bugs** — `tsc --noEmit --strict` gibt in beiden Armen 0 Errors.
   Das ist das stärkste Ergebnis: Argument-Parsing-Bugs dieser Art sind für den Compiler
   vollständig unsichtbar. Nur Ausführung mit echten Inputs macht sie sichtbar.

2. **Bug-Trigger-Selektivität** — Der Bug tritt nur bei Flag-Wert-Pairs (`--flag value`) auf,
   nicht bei positional args oder letztem Flag. Input 1 und 2 bleiben korrekt; 3 und 4 fallen.

3. **Latenz-Problem** — Input 5 hat einen unsichtbaren Bug (transform übersprungen). Das zeigt:
   `hidden_bugs_count` kann underversen wenn die Test-Inputs keine differenzierenden Erwartungen haben.

4. **Fix-Scope ist klar** — cli.ts, 7 Zeilen. Unabhängig vom Fix-Modus.

### Was nicht direkt gemessen werden konnte

- **time_to_fix ohne Modell-Leakage** — Als KI-Agent mit Kontext über den Bug war weder
  guided noch unguided eine echte Discovery-Messung. Beide = 1 Iteration.
- **first_failing_input_index als Vergleichsmetrik** — Single-Shot war bug-frei; Vergleich
  ist methodisch nicht korrekt.

### Was Interpretation bleibt

- Ob die Modul-Isolation von `cli.ts` einen menschlichen Entwickler beim Bug-Finden
  schneller macht, ist plausibel aber nicht gemessen.
- Ob die bug-freie Single-Shot-Variante auf die Generierungsstrategie oder Zufall
  zurückzuführen ist, bleibt offen. Single-Shot könnte mit anderem Modell/Prompt
  auch Bugs produzieren.

## Verdict

**inconclusive** — mit zwei qualifizierten Befunden:

1. **Compiletransparenz bestätigt**: Laufzeitbugs im Argument-Parser sind für den
   TypeScript-Compiler unsichtbar. Das gilt für beide Arme gleichermaßen.

2. **Fix-Lokalisierung bestätigt**: Der Fix im Incremental-Arm ist auf `cli.ts` beschränkt.
   Das entspricht der Design-Erwartung. Ob das einen Debuggability-Vorteil bietet, ist
   abhängig vom Suchverhalten des Fixers.

Hypothese nicht prüfbar: Der primäre Vergleich (`first_failing_input_index`) scheitert am
Sonderfall "bugfreie Kontrolle". Das ist nicht ein Versagen des Experiments, sondern ein
Hinweis, dass das Design für diesen Fall eine Ausnahmeregel braucht.

## Lessons Learned

1. **Sonderfall "bugfreie Kontrolle" muss geregelt sein** — wenn ein Arm keine Bugs hat,
   ist `first_failing_input_index` nicht vergleichbar. Erfolgskriterien müssen diesen Fall
   explizit behandeln (z.B. `hidden_bugs_count` als Fallback-Primärmetrik).

2. **Modell-Leakage ist real und messwirksam** — Ein KI-Agent mit Kontext über den Bug kann
   `time_to_fix` nicht unvoreingenommen messen. Für eine belastbare Messung: independent agent
   oder human developer ohne Prior.

3. **Latente Bugs brauchen differenzierende Test-Inputs** — Input 5 hat eine Uppercase-Transform
   auf numerische Werte, die keinen sichtbaren Effekt hat. Für vollständige Abdeckung:
   Text-Werte in allen Transform-Szenarien.

4. **Compilation ist kein Debugging-Proxy** — Stärkste Bestätigung des gesamten Experiments:
   `tsc --strict` findet diese Bug-Klasse nicht. Runtime-Tests sind zwingend.

5. **Modularisierung begrenzt Patch-Scope** — `cli.ts` ist die Fix-Datei. Das ist inhärent
   richtig für diesen Bug-Typ. Ob ein Entwickler `cli.ts` ohne Hint findet, hängt vom
   Dateinamen und der Modul-Benennung ab — was in diesem Fall gut ist (`cli.ts` ist selbstbeschreibend).

## Nächste Schritte

Für eine Folgestudie mit höherem Erkenntnisgewinn:
1. **Sonderfall regeln**: Erfolgskriterien um "wenn ein Arm bug-frei ist" erweitern
2. **Kontaminationskontrolle**: Human-Developer oder frischer Agent ohne Bug-Vorwissen
3. **Symmetrischer Vergleich**: Single-Shot-Arm mit äquivalentem Bug vorbereiten
4. **Differenzierende Test-Inputs**: Keine no-op Transforms; alle Inputs sollen beobachtbare Ausgaben haben
5. **Zweiter Task**: Dieser Singlepoint könnte atypisch sein (Arg-Parser-Bug ist spezifisch)
