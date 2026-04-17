## Experiment Run

### PR-Typ

- [ ] experiment_run
- [ ] experiment_review
- [ ] experiment_reconciliation

### Experiment
- **Name:** <!-- Experiment-Name -->
- **Ordner:** `experiments/<name>/`
- **Hypothese:** <!-- Kurzbeschreibung der Hypothese -->
- **Issue-Referenz:** <!-- #Nr -->

### Checkliste

- [ ] `manifest.yml` ist vollständig ausgefüllt
- [ ] `method.md` beschreibt das Vorgehen
- [ ] `CONTEXT.md` dokumentiert den Ausgangszustand
- [ ] `INITIAL.md` dokumentiert die initiale Prompt-/Setup-Situation
- [ ] `evidence.jsonl` enthält maschinenlesbare Beobachtungen
- [ ] `results/decision.yml` nutzt gültige Decision-Type-Separation:
	`result_assessment` → `confirms | refutes | mixed | inconclusive`
	`adoption_assessment` → `adopt | reject | defer`
- [ ] `results/result.md` fasst die Ergebnisse zusammen

### Ergebnis
<!-- Kurzzusammenfassung: Was wurde beobachtet? Was ist das Verdict? -->

### Reconciliation (falls zutreffend)

- [ ] Keine neuen Execution-Claims hinzugefügt
- [ ] Manifest auf evidenztragenden Zustand zurückgeführt
- [ ] Iteration korrekt als prepared markiert (falls nicht ausgeführt)

### Nächste Schritte
<!-- Iterate? Promote? Archive? -->
