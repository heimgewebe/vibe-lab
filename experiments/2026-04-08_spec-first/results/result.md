---
title: "Spec-First Vibe-Coding — Ergebnis"
status: adopted
canonicality: operative
relations:
  - type: validates
    target: ../../../catalog/techniques/spec-first-prompting.md
---

# result.md — Spec-First Vibe-Coding

> **Einstufungshinweis (Altbestand):** Diese Adoption wurde rekonstruktiv eingestuft.
> `execution_status: reconstructed` und `adoption_basis: reconstructed` bedeuten:
> die Adoption fußt auf historisch dokumentierter Plausibilität (Beobachtungen, Ergebnisbericht),
> nicht auf einem erfassten Execution-Proof (`run_meta.json`).
> Reconstructed Adoption ist zulässig, aber kein Goldstandard — neue Adoptionen ab v2 verlangen
> `adoption_basis ∈ {executed, replicated}`. Siehe `docs/blueprints/blueprint-v2.md` → Übergangsregel.

## Zusammenfassung

Spec-First-Prompting — das Voranstellen eines formalen Spezifikationsschritts vor der Code-Generierung — verbessert Konsistenz, Vollständigkeit und subjektiven Flow messbar. In allen drei Tasks schnitt der Spec-First-Ansatz besser ab als die direkte Beschreibung.

## Beobachtungen

### Wirksamkeit (Effektivität)
- **Fehlercodes:** Spec-First lieferte in 2/3 Tasks alle erwarteten HTTP-Statuscodes; Direct fehlten jeweils 2 relevante Codes.
- **Validierung:** Spec-First erzwang explizite Definition aller Validierungsregeln; Direct überging Edge Cases.
- **Konsistenz:** Spec-First erzeugte einheitliche Response-Envelopes; Direct war inkonsistent.

### Reibung (Aufwand)
- **Prompts:** Spec-First benötigt 2 Schritte statt 1, aber der Gesamtaufwand sinkt durch weniger Nacharbeit.
- **Nacharbeit:** 4 Zeilen (Spec-First) vs. 23 Zeilen (Direct) bei Task 1 — Faktor 5-6× weniger.

### Flow (subjektive Qualität)
- **Lesbarkeit:** 4.3/5 (Spec-First) vs. 3.7/5 (Direct)
- **Vertrauen:** 4.0/5 (Spec-First) vs. 2.7/5 (Direct) — der deutlichste Unterschied.

## Verdict

**Adopted.** Spec-First-Prompting wird als Technique in den Katalog aufgenommen.

## Lessons Learned

1. Der Spec-Schritt zwingt zur Präzisierung — die eigentliche Qualitätsverbesserung entsteht nicht durch die Spec selbst, sondern durch den Denkprozess.
2. OpenAPI eignet sich besonders gut als Spec-Format für REST-APIs; für andere Domänen (CLI, UI) müssen andere Spec-Formate evaluiert werden.
3. Die kleine Stichprobe (3 Tasks, 1 Modell, 1 Person) begrenzt die Generalisierbarkeit. Ein Follow-up-Experiment mit anderem Modell ist empfehlenswert.

## Nächste Schritte

- ✅ Promotion-PR für Katalogeintrag
- ✅ Adopted Prompt erstellen
- ⬜ Follow-up: Test mit Claude 3.5 Sonnet

## Interpretation Budget

### Allowed Claims
- Spec-First-Prompting verbessert Konsistenz und Vollständigkeit bei REST-API-Generierung im getesteten Setup (3 Tasks, GPT-4, 1 Person).
- Der Spezifikationsschritt erzwingt eine Präzisierung, die Nacharbeit messbar reduziert (Faktor 5–6× weniger Zeilen bei Task 1).
- OpenAPI eignet sich als Spec-Format für REST-API-Tasks.

### Disallowed Claims
- Spec-First ist generell überlegen – die Studie ist zu klein (3 Tasks, 1 Modell, 1 Person) für generelle Aussagen.
- Das Ergebnis überträgt sich direkt auf andere Domänen (CLI, UI, non-REST-APIs) oder andere LLMs.
- Spec-First ist immer die optimale Strategie – bei sehr einfachen Tasks kann der Overhead überwiegen.
- Die Adoption ist ein Goldstandard-Befund – sie basiert auf rekonstruierter Evidenz (kein run_meta.json).

### Evidence Basis
- Direkt beobachtet: Fehlercodes, Validierungsregeln, Konsistenz von Response-Envelopes, Nacharbeit-Zeilenzahl, subjektive Flow-Scores (3 Tasks)
- Indirekt gestützt: Bestätigt durch 2026-04-14_prompt-length-control (kausale Kontrollstudie)
- Nicht getestet: Andere LLMs, andere Domänen, größere Task-Stichproben, Team-Settings
