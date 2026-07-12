---
title: "Tool-Export-Entscheidung"
status: active
canonicality: navigation
updated: "2026-07-12"
relations:
  - type: references
    target: ../../docs/foundations/repo-plan.md
---

# Tool-Exporte: stillgelegt, Kompatibilität erhalten

Die automatischen Cursor- und Copilot-Projektionen sind stillgelegt. Vibe-Lab
veröffentlicht dort keine kopierten Instruction Blocks mehr, weil für diese
Flächen kein hinreichend genutzter Downstream-Consumer belegt ist.

Die vorhandenen Dateipfade bleiben vorerst als kleine, deterministisch erzeugte
Kompatibilitätsmarken bestehen. Dadurch bleiben alte Links nachvollziehbar, ohne
eine zweite aktive Anweisungswahrheit zu erzeugen.

## Reaktivierungsgate

Eine Tool-Projektion darf erst wieder aktive Anweisungen enthalten, wenn vorab
alle folgenden Punkte feststehen:

1. benannter Downstream-Consumer und konkrete Verwendung;
2. reviewed Entscheidungsziel mit Owner;
3. messbare Erfolgs- und Falsifikationskriterien;
4. Review- und Ablaufdatum;
5. Nachweis, dass die Projektion gegenüber der kanonischen Quelle realen Nutzen
   erzeugt und nicht nur Pflege- oder Driftkosten.

Bis dahin sind `exports/copilot/` und `exports/cursor/` reine
Kompatibilitätsflächen ohne operative Autorität.
