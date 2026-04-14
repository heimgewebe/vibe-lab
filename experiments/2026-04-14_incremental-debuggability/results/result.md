---
title: "Incremental vs. Single-Shot: Debuggability — Ergebnis"
status: designed
canonicality: operative
---

# result.md — Experiment-Ergebnis

> **Status: designed — noch nicht ausgeführt.**
> Dieses Dokument wird nach Abschluss der Ausführungsphase befüllt.
> Struktur ist als Orientierungsrahmen für die spätere Dokumentation angelegt.

## Zusammenfassung

<!-- Nach Ausführung: Kurze Zusammenfassung der Ergebnisse.
     Was wurde beobachtet? Welche Strategie erkannte Bugs früher? -->

## Beobachtungen

### Wirksamkeit (Bug-Detection)

<!-- Tabelle mit Primärmetriken nach Ausführung:

| Metrik                       | Single-Shot | Incremental | Δ |
| ---------------------------- | ----------- | ----------- | - |
| time_to_first_bug_detection  | ?           | ?           | ? |
| time_to_fix (Prompts)        | ?           | ?           | ? |
| hidden_bugs_count            | ?           | ?           | ? |
| patch_size (Zeilen)          | ?           | ?           | ? |
| correct_outputs (5 Inputs)   | ?/5         | ?/5         | ? |
-->

### Reibung (Ausführungsaufwand)

<!-- Wie aufwändig war das Ausführen, Bug-Finden und Fixen? -->

### Modulare Fix-Barkeit

<!-- War das Fixen in Incremental einfacher wegen Modul-Isolation?
     Oder war der Aufwand vergleichbar? -->

## Deutung

<!-- Nach Ausführung: Was bedeuten die Metriken?
     Trennen: Was ist messbar belegt — was ist Interpretation?
     Besonders: Ist ein Vorteil von Incremental auf Modul-Isolation zurückzuführen
     (struktureller Effekt) oder auf die Incremental-Strategie an sich? -->

## Verdict

<!-- adopted / rejected / inconclusive — nach Ausführung -->

## Lessons Learned

<!-- Was wurde gelernt, unabhängig vom Verdict?
     Insbesondere: Schärft diese Messung die Decision Rule
     (trivial → Single-Shot, mittel → Incremental, kritisch → Spec-First + Incremental)? -->

## Nächste Schritte

<!-- Nach Ausführung:
     - Bei inconclusive: Weiteres Task isolieren (Task 1 oder Task 3)?
     - Bei bestätigt: Catalog-Eintrag für Decision Rule vorbereiten?
     - Immer: Verbesserungen der Messmethodik dokumentieren -->
