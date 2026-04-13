---
title: "Manifest-Audit: Methode"
status: testing
canonicality: operative
---

# method.md — Manifest-Audit

## Hypothese

Ein kurzes Audit-Skript (~60 LOC Python) kann Inkonsistenzen zwischen dem deklarierten
`execution_status` in `manifest.yml` und dem tatsächlichen Zustand der `evidence.jsonl`-Dateien
automatisch erkennen. In den vorhandenen Experimenten wird es mindestens eine solche
Inkonsistenz finden.

## Methode

### Vorgehen

1. Skript schreiben (`artifacts/audit.py`), das alle `experiments/*/manifest.yml` einliest
2. Für jedes Experiment ermitteln:
   - Deklarierter `execution_status` (Feld in manifest.yml, kann fehlen)
   - Anzahl Einträge in `results/evidence.jsonl` (kann fehlen oder leer sein)
   - Ob `execution_refs` befüllt sind
3. Inkonsistenz-Regeln anwenden (siehe unten)
4. Ausgabe: tabellarische Übersicht aller Experimente + Markierung von Inkonsistenzen
5. Beobachtungen in `results/evidence.jsonl` festhalten

### Inkonsistenz-Regeln

| Situation | Bewertung |
|-----------|-----------|
| `execution_status` fehlt, aber `evidence.jsonl` hat Einträge | Inkonsistenz: Ausführung nicht deklariert |
| `execution_status: executed`, aber leere/fehlende `evidence.jsonl` | Inkonsistenz: Behauptete Ausführung ohne Spur |
| `execution_status: designed/prepared`, aber `evidence.jsonl` hat Einträge | Inkonsistenz: Evidenz ohne Statusupdate |
| `execution_status: executed`, aber kein `execution_refs`-Eintrag | Inkonsistenz (vom Schema erzwungen) |
| Alles konsistent | OK |

### Metriken

- Anzahl gefundener Inkonsistenzen (absolut)
- Arten der Inkonsistenz (welche Regel greift)
- Falsch-positiv-Rate: Fälle, in denen das Skript etwas als Inkonsistenz markiert, die eigentlich vertretbar ist

### Erfolgskriterien

- **Bestätigt:** ≥1 echte Inkonsistenz gefunden, keine falschen Ausgaben, Skript läuft fehlerfrei
- **Widerlegt:** Keine Inkonsistenzen gefunden trotz fehlender `execution_status`-Felder (Schema reicht aus)
- **Inconclusive:** Skript findet etwas, aber unklar ob es echte Inkonsistenzen oder Designentscheidungen sind

## Variablen

| Variable | Beschreibung | Wert |
|---|---|---|
| Eingabe | Alle Experimente in `experiments/` | 3 nicht-template Experimente |
| Kontrolle | Keine (rein beschreibend) | — |
| Metrik 1 | Anzahl Inkonsistenzen | gemessen |
| Metrik 2 | Fehlerfreie Skriptausführung | ja/nein |

## Risiken und Einschränkungen

- Das Skript ist selbst Teil des Experiments → Implementierungsfehler im Skript verfälschen Ergebnisse
- PyYAML-Parsing könnte Felder anders interpretieren als erwartet
- `_template`-Ordner muss explizit ausgeschlossen werden
