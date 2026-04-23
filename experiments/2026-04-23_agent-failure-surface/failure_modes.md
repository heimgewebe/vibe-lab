---
title: "Failure Modes: Agent Failure Surface Mapping"
status: draft
canonicality: operative
created: "2026-04-23"
updated: "2026-04-23"
author: "Claude Opus 4.7"
---

# Failure Modes — Agent Failure Surface Mapping

> **Status:** Design-Stand. Dieses Dokument wird je Phase-PR fortgeschrieben.
> Die unten gelisteten Punkte sind **Risiken der Reihe selbst**, nicht
> Befunde aus Experimentläufen. Ergebnis-Failure-Modes werden pro Phase in
> `results/` und anschließend hier konsolidiert.

## Wann funktioniert diese Experimentreihe NICHT?

- **Ohne CI-Strikte:** Wenn `make validate` nicht als harte Wahrheit gilt,
  sind Fixture-Änderungen reine Dokumentation ohne Durchschlagskraft.
- **Ohne Modell-Disziplin:** Wenn Phase-Läufe Modell/Temperatur/Seed nicht
  protokollieren, lässt sich Toleranz nicht von Modell-Varianz trennen.
- **Bei reinem Einzelfall-Fokus:** Wenn Fixtures auf konkrete
  Drift-Instanzen statt auf Äquivalenzklassen zielen, entsteht Overfitting
  statt Härtung.
- **Ohne sofortige Operationalisierung:** Wenn Phasen nur beobachten und
  keine Fixture/Test/Validator-Änderung erzeugen, kippt die Reihe in
  epistemische Prokrastination.

## Bekannte Fehlannahmen (Design-Zeit)

- **Annahme A:** Die Fixture-Matrix beschreibt den Ist-Zustand vollständig.
  Risiko: Matrix könnte unvollständig sein (dokumentierte Gaps ≠ tatsächliche
  Gaps). Gegenmittel: Phase 1 beginnt mit Inventur, nicht mit Injektion.
- **Annahme B:** Aktuelle Validatoren sind deterministisch gegenüber
  Whitespace-/Unicode-Varianten. Nicht geprüft — Phase 1 muss dies belegen.
- **Annahme C:** Cross-Contract-Validatoren decken semantische Widersprüche
  konzeptuell ab. Tatsächliche Abdeckung ist phaseweise zu verifizieren.
- **Annahme D:** Dry-Run-Replay ist repräsentativ genug für Validierungs­
  semantik. Phase 4 stellt diese Annahme explizit in Frage — ohne Anspruch
  auf quantitative Auflösung.

## Grenzen der Evidenz

- **Stichprobengröße:** Pro Phase ≥ 4–8 konstruierte Fälle. Das reicht für
  Existenz-Nachweise („mindestens eine Toleranz gefunden"), nicht für
  Verteilungsaussagen.
- **Kontext-Abhängigkeit:** Reihe testet Schema- und Validator-Verhalten
  unter kontrollierten Fixture-Bedingungen, nicht unter realer Agentenlast.
- **Selbst-Selektion:** Der Designer der Injektionsfälle (Claude Opus 4.7)
  kennt die bestehenden Validatoren; blinde Cross-Reviews durch ein anderes
  Modell sind empfohlen, aber nicht Pflicht.
- **Replay-Phase bleibt qualitativ:** Ohne echten Runner (Phase F) ist
  Phase 4 argumentativ. Das ist explizit als Einschränkung festgehalten
  und nicht als Schwäche zu reinterpretieren.

## Risiko einer Fehlanwendung

- **Scheintreffer-Gefahr:** Wenn eine Phase einen unerkannten Drift
  findet, aber die Konsequenz nur den konkreten Testfall abdeckt (nicht
  die Klasse), entsteht falsche Härtungs-Sicherheit. Gegenmittel:
  Äquivalenzklassen müssen in Fixtures dokumentiert und in der Matrix
  namensstabil verankert sein.
- **Overhardening:** Zu viele neue Constraints können benign Agent-Varianz
  blockieren. Jede Validator-Änderung muss durch mindestens **zwei**
  Fixtures motiviert sein (ein positiver + ein negativer).
- **„Nice to know"-Creep:** Reihe kann sich in Unterscheidungen verlaufen,
  die für Agent-Korrektheit irrelevant sind. Stop-Kriterium:
  Phase-PR bleibt ohne verankerte Fixture → Phase wird als `inconclusive`
  geschlossen, nicht verlängert.

## Negativ-Evidenz ist explizit gültig

Eine Phase, die zeigt, dass **keine** neue Toleranz gefunden wurde, ist ein
gültiges Ergebnis — vorausgesetzt, die Diagnose + Injektion sind in
`evidence.jsonl` belegt. Solche Ergebnisse werden hier im Dokument unter
„Bestätigte Schärfe" geführt und in der Fixture-Matrix als
`covered; verified 2026-…` markiert.
