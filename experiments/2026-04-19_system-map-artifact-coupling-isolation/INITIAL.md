---
title: "Initiale Situation: System-Map Artifact Coupling Isolation"
status: draft
canonicality: operative
---

# INITIAL.md — Initiale Situation

## Ausgangspunkt

Der Experimentierende startet von einem sauberen Branch-Zustand auf `main` (oder einem
frischen Branch), mit:

- `make generate && make validate` = grün (kein stale, keine Fehler)
- Kein uncommitted change
- `docs/_generated/system-map.md` aktuell (entspricht `git ls-files`-Stand)

## Gegenlauf-Setup (Testfall T-1: Workflow-Isolation)

Um die Workflow- vs. Boundary-Hypothese zu trennen, wird ein minimaler PR durchgeführt,
der **keine neuen Run-Artefakte** unter `artifacts/run-*/` hinzufügt:

```
1. Branch: exp/run-007-no-artifact-write (oder äquivalent)
2. Änderung: eine kleine canonical-source-Änderung in einem bestehenden Dokument
   (z.B. ein Wort in docs/foundations/vision.md oder docs/foundations/repo-plan.md)
3. make generate (einmal)
4. make validate
5. git add + commit (nur die canonical source + regenerierte derived files)
6. PR öffnen
7. CI beobachten: tritt stale system-map.md auf oder nicht?
```

Entscheidend: Schritt 2 enthält **kein** `mkdir artifacts/run-007/` und **kein**
Schreiben neuer Dateien unter `artifacts/run-*/`.

## Systemkonfiguration

- `make generate` = ruft alle Generator-Skripte inkl. `generate_system_map.py` auf
- `generate_system_map.py` zählt Dateien via `git ls-files`
- GitHub Actions CI: `.github/workflows/validate.yml` (oder äquivalent)

## Erwartete Baseline (ohne den Gegenlauf)

Ohne Gegenlauf würde eine normale Run-Dokumentation mit neuen Artefakten den bekannten
stale-Pfad triggern (belegt in Run-003 bis Run-006 des Predecessor-Experiments).

## Bekannte Constraint

Kein echter Lauf wurde zum Zeitpunkt der Anlage dieses Experiments durchgeführt.
Dieser Abschnitt dokumentiert den designierten Ausgangspunkt — nicht einen belegten.
`execution_status: designed` gilt bis zur artefaktgetragenen Ausführung.
