# artifacts/ — Laufzeitartefakte

Dieser Ordner nimmt strukturierte Run-Artefakte auf, sobald echte Testläufe durchgeführt werden.

## Erwartete Struktur (wenn Testläufe ausgeführt)

```
artifacts/
  run-T1-no-artifact-write/
    run_meta.json       # Pflicht: Execution-Proof
    execution.txt       # CI-Output, Commit-Hash, Zeitstempel
  run-T2-with-artifact-write/   # optional (aus Predecessor ggf. als Referenz)
    run_meta.json
    execution.txt
```

## Aktueller Status

**Kein Run ausgeführt.** `execution_status: designed` gilt bis zur belegten Ausführung.

Dieses Verzeichnis ist leer, bis T-1 (Gegenlauf ohne Artifact-Write) mit echtem
Execution-Proof dokumentiert ist. Keine Pseudo-Ausführung, keine Platzhalter-Artefakte.
