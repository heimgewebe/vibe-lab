---
title: "Failure Modes: System-Map Artifact Coupling Isolation"
status: draft
canonicality: operative
---

# Failure Modes — System-Map Artifact Coupling Isolation

## Wann funktioniert dieses Testdesign NICHT?

- [x] **Wenn T-1 einen anderen Branch-Ausgangszustand hat als die Predecessor-Runs.**
  Dann ist der Vergleich nicht sauber, weil weitere canonicale Änderungen das Ergebnis
  überlagern könnten.

- [x] **Wenn im T-1-Branch doch Artefaktdateien committet werden (Verwechslung).**
  Der Testfall kollabiert zur T-2-Replik. `artifact_write_performed` muss explizit
  auf false gesetzt und im Commit-Log prüfbar sein.

- [x] **Wenn `generate_system_map.py` zwischenzeitlich geändert wurde.**
  Dann unterscheiden sich T-1 und die Predecessor-Runs in der Zähllogik — die Trennung
  wäre nicht mehr auf Workflow/Boundary reduzierbar, sondern auch durch Implementierungsänderung
  erklärbar.

- [x] **Wenn GitHub Actions-CI andere Checks ausführt als lokal.**
  Lokal-grün reicht nicht als Beweis für CI-grün. Entscheidend ist das CI-Ergebnis.

## Bekannte Fehlannahmen

- [x] **Fehlannahme: T-2 ist aus dem Predecessor vollständig abgedeckt.**
  Run-003 bis Run-006 belegen das stale-Muster nach Artifact-Write, aber der
  Branch-Kontext war jeweils unterschiedlich. Identische Vergleichsbedingungen
  zu T-1 wären nötig für strikte Kontrolle.

- [x] **Fehlannahme: Ein einzelner T-1-Lauf beweist H1 oder H2.**
  Ein Lauf ist ein Datenpunkt. H1 und H2 bleiben nach einem Lauf Hypothesen mit
  unterschiedlicher Stützung, nicht bewiesene Tatsachen.

- [x] **Fehlannahme: Workflow-Disziplin allein löst das Problem wenn H1.**
  Selbst wenn H1 stimmt (Reihenfolge als Trigger), bleibt die Frage offen, ob
  die Kopplung (run-Artefakte fließen in canonical diagnostics) gewollt ist.
  H1 und H2 schließen sich nicht vollständig aus.

## Grenzen der Evidenz

- **Stichprobengröße:** Dieses Experiment ist auf minimale Testfälle angelegt (T-1, ggf. T-2).
  Statistische Absicherung nicht möglich; Replikation bleibt offen.
- **Kontext-Abhängigkeit:** Nur im `vibe-lab`-Repo getestet; andere Repo-Strukturen
  mit anderen Generator-Setups können andere Verhalten zeigen.
- **Zeitpunkt:** Generator-Logik kann sich ändern; Beobachtungen gelten für den
  Zustand zum Zeitpunkt der Ausführung.

## Risiko einer Fehlanwendung

Wenn aus einem einzigen T-1-Ergebnis (kein stale ohne Artifact-Write) vorschnell
geschlossen wird: "Das Problem ist nur Workflow, keine Architekturüberlegung nötig" —
dann ignoriert das den H2-Anhaltspunkt: `git ls-files` hat per Design keinen
Scope-Filter. Auch wenn T-1 H1 stützt, bleibt die Boundary-Frage (soll das so sein?)
eine separate, legitime Designfrage.

**Kurzform:** Kausaltrennung ≠ Designentscheidung. Ein zuverlässig wiederholter
Reihenfolge-Fehler ist noch keine Antwort auf die Frage, ob die Kopplung gewollt ist.
