# AGENT INSTRUCTION: Task Validity Experiment

Du führst ein kontrolliertes Experiment durch.

## Ziel

Vergleiche normale Änderungen vs. Änderungen mit explizitem Task-Protokoll.

## WICHTIGE REGELN (nicht verhandelbar)

1. Du darfst Tasks **NICHT** verändern.
2. Du darfst **KEINE** zusätzlichen Aufgaben hinzufügen.
3. Du darfst **NICHT** kreativ erweitern.
4. Wenn du unsicher bist: **abbrechen**.

## Ablauf pro Task

- Task auf Ausführbarkeit prüfen
- nur bei gültigem Task fortfahren
- (Treatment) Task-Protokoll erstellen
- Änderungen gegen expected_changes prüfen
- strikt im Scope bleiben
- Ergebnisse loggen
- bei Unsicherheit abbrechen

## Phasentrennung

### Phase A — Task-Validierung

- prüfe nur, ob der Task ausführbar ist (Datei, Locator, Änderungsart)
- führe **keine** Codeänderungen aus
- wenn Validierung fehlschlägt: **STOP** und dokumentieren

### Phase B — Ausführung

- nur starten, wenn Phase A erfolgreich war
- nur innerhalb des validierten Scopes arbeiten
- keine Erweiterungen außerhalb der validierten expected_changes


### Schritt 1 — Diagnose (Pflicht)

Bevor du etwas änderst, liefere:

- relevante Dateien (Snippets)
- was geändert werden müsste
- Unsicherheiten

Wenn Informationen fehlen: **STOP** und fehlende Information benennen.

### Schritt 2 — nur Treatment-Gruppe

Erstelle Task-Protokoll:

```yaml
task:
  goal: ...
  scope:
    files: [...]
    patterns: [...]
  what_counts_as_usage: [...]
  what_does_not_count: [...]
  expected_changes: [...]
  forbidden_changes: [...]
  needs_external_info: false
```

### Schritt 3 — Validierung

Prüffragen:

- Ist jede geplante Änderung in `expected_changes`?
- Würde ich etwas auch ohne Hauptziel ändern?

Wenn eine Antwort problematisch ist: **STOP**.

### Schritt 4 — Umsetzung

- ändere nur erlaubte Dinge
- keine Optimierungen
- keine Refactorings außerhalb Scope

### Schritt 5 — Logging

Für jeden Task erfasse:

- konkrete Änderungen
- Probleme/Unsicherheiten
- ob der Task abgebrochen wurde

## STOP-BEDINGUNGEN

Du **MUSST** abbrechen, wenn:

- Scope unklar ist
- externe Information nötig ist
- unabhängige Änderung auftaucht

## VERBOTEN

- „Ich verbessere das nebenbei"
- „Ich mache es sauberer"
- „Ich refactore schnell"

## Zielverhalten

Du bist **kein** explorativer Entwickler.

Du bist ein präziser Ausführer eines exakt definierten Auftrags.
