---
title: "Failure Modes — Agent/Skill Minimal Layer Instrumentation"
status: draft
canonicality: operative
---

# Failure Modes — Agent/Skill Minimal Layer Instrumentation

## Wann funktioniert diese Instrumentierung NICHT?

- [ ] **Wirksamkeit aus einem einzigen PR ableiten** — Ein PR ist kein Beweis. Jeder Effektclaim auf Basis eines einzelnen Datenpunkts ist methodisch unzulässig.
- [ ] **Fehlende Kontrollgruppe übersehen** — Ohne Baseline-PRs ohne Agent-Schicht ist kein Vergleich möglich. Deskriptive Daten ≠ kausale Daten.
- [ ] **Nicht vergleichbare PRs mischen** — PRs mit unterschiedlichen Aufgabentypen, Komplexitätsstufen oder Modellen sind nur vergleichbar, wenn diese Variablen annotiert und kontrolliert werden.
- [ ] **Auditor nicht tatsächlich nutzen** — Wenn der evidence-reconciliation-auditor im PR-Prozess übergangen wird, ist die Instrumentierung nicht aktiv. Das Vorhandensein des Agents ≠ seine Nutzung.
- [ ] **Metriken unterschiedlich zählen** — Wenn `scope_drift_count` oder `unsupported_claim_count` je PR unterschiedlich definiert werden, sind die Datenpunkte nicht vergleichbar.
- [ ] **False Blocks nicht erfassen** — Wenn der Auditor oder Critic einen PR ungerechtfertigt blockiert und dieser Vorfall nicht als `false_block_count` dokumentiert wird, entsteht ein verzerrtes Bild der Schicht-Performance.
- [ ] **Zeitmetrik kausal fehlinterpretieren** — `task_completion_time_observed` ist eine deskriptive Beobachtung. Sie darf nicht als Beweis für Beschleunigung oder Verlangsamung durch die Agent-Schicht interpretiert werden.
- [ ] **Skill-Dateien bewerten, obwohl keine dedizierten Skill-Dateien existieren** — Es wurden keine Skill-Dateien als eigenständiger Repo-Artefakttyp eingeführt. Jede Aussage über die Wirkung von Skill-Dateien ist ohne Grundlage.
- [ ] **Auditor-Verdicts ohne Evidence-Pointer archivieren** — Jeder Auditor-Befund muss auf einen konkreten Artefakt-Rückverweis zeigen. Verdicts ohne `artifact_ref` oder nachvollziehbaren Belegerefund sind epistemisch wertlos.

## Bekannte Fehlannahmen

- [ ] Die Annahme, dass der Auditor zuverlässig genutzt wird, wenn er nur verfügbar ist.
- [ ] Die Annahme, dass Metriken selbsterklärend sind — ohne klare Zähldefinition entstehen Inkonsistenzen.
- [ ] Die Annahme, dass das Experimentgerüst selbst schon einen Effekt hat.

## Grenzen der Evidenz

- **Stichprobengröße:** Null reale PR-Datensätze zum Startzeitpunkt. Mindestens drei vergleichbare PRs nötig für ein Zwischenergebnis.
- **Kontext-Abhängigkeit:** Nur in vibe-lab getestet; andere Repositories, Modelle oder Team-Konstellationen können abweichen.
- **Selbst-Selektion:** Aufgaben, bei denen der Auditor genutzt wird, können systematisch anders sein als Aufgaben, bei denen er übergangen wird.

## Risiko einer Fehlanwendung

Wenn dieses Instrumentierungs-Experiment als Wirksamkeitsnachweis gelesen wird, entstehen Fehlannahmen über die Agent-Schicht. Das Gerüst ist ein Messrahmen — kein Urteil. Jede Ableitung über Nutzen oder Schaden der Schicht auf Basis dieses Experiments allein ist methodisch unzulässig.
