---
title: "Incremental vs. Single-Shot: Debuggability — Initiale Situation"
status: designed
canonicality: operative
---

# INITIAL.md — Initiale Situation

## Ausgangspunkt

Beide Varianten von Task 2 liegen bereits vor:
- **Single-Shot:** `experiments/2026-04-14_incremental-refinement/artifacts/task2-single-shot/index.ts`
- **Incremental:** `experiments/2026-04-14_incremental-refinement/artifacts/task2-incremental/` (7 Dateien)

Beide Varianten wurden im Vorgängerexperiment mit `tsc --noEmit --strict` validiert (0 Errors).
Die Incremental-Variante enthielt einen CLI-Parser-Bug (doppeltes `i++`), der nachträglich gefixt wurde.

**Für dieses Experiment** wird eine neue, unberührte Kopie beider Varianten angelegt:
```
experiments/2026-04-14_incremental-debuggability/artifacts/task2-single-shot/
experiments/2026-04-14_incremental-debuggability/artifacts/task2-incremental/
```

Der **bekannte Bug** im Incremental-Arm wird für die Execution-Phase absichtlich wieder eingeführt
(Reverted auf den Bug-Stand), um die ursprüngliche Fehlerverteilung zu rekonstruieren und
Bug-Detection zu messen.

## Definierte Test-Inputs (5 Szenarien)

Diese 5 CSV-Testdateien werden für beide Varianten identisch genutzt:

### Input 1 — Basisfall

```
name,age,city
Alice,30,Berlin
Bob,25,Hamburg
Charlie,35,München
```
Befehl: `csv-tool input.csv`
Erwartetes Ergebnis: CSV unverändert ausgegeben

### Input 2 — Uppercase-Transform

```
name,age,city
Alice,30,berlin
Bob,25,hamburg
```
Befehl: `csv-tool input.csv --transform city:uppercase`
Erwartetes Ergebnis: city-Spalte in Großbuchstaben

### Input 3 — Flag mit Wert (Bug-Trigger für Incremental)

```
name,age,city
Alice,30,Berlin
Bob,25,Hamburg
```
Befehl: `csv-tool --input input.csv --format json`
Erwartetes Ergebnis: JSON-Ausgabe
**Bug-Relevanz:** Dieser Befehl triggert das `--format`-Flag mit Wert — der doppelte `i++`-Bug
überspringt `json` und liest stattdessen das nächste Argument oder undefined.

### Input 4 — Mehrere Flags (Bug-Kaskade)

```
name,score,category
Product A,85,Electronics
Product B,92,Books
Product C,71,Electronics
```
Befehl: `csv-tool --input input.csv --format json --columns name,score`
Erwartetes Ergebnis: JSON mit name und score für alle Zeilen
**Bug-Relevanz:** Mehrere Flags mit Werten — Bug-Kaskade wahrscheinlich.

### Input 5 — Filter + Transform (Kombination)

```
name,department,salary
Alice,Engineering,90000
Bob,Marketing,70000
Charlie,Engineering,85000
```
Befehl: `csv-tool input.csv --filter department=Engineering --transform salary:uppercase`
Erwartetes Ergebnis: Nur Engineering-Zeilen, salary uppercase

## Systemkonfiguration

- Node.js: >= 18.x
- TypeScript: 5.3 (tsc oder ts-node)
- Ausführung: `ts-node index.ts <args>` oder `tsc && node dist/index.js <args>`
- Kein Mocking; reale Datei-I/O

## Erwartete Baseline

Beide Varianten kompilieren korrekt. Single-Shot wird auf Input 1–5 korrekt reagieren.
Incremental wird auf Input 3 und 4 (mehrere Flags mit Wert) fehlerhaft reagieren —
entweder falsches Output oder Runtime-Error.

Die Baseline-Erwartung: Incremental-Arm mit Bug hat mindestens 2/5 Inputs mit falschen Ergebnissen.
