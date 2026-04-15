## Promotion — Aufnahme in die Bibliothek

### Ziel
- [ ] **Catalog Entry** in `catalog/`
- [ ] **Combo** in `catalog/combos/`
- [ ] **Prompt** in `prompts/adopted/`

### Referenzen
- **Experiment:** `experiments/<name>/`
- **Issue:** #<!-- Nr -->
- **Evidenz:** `experiments/<name>/results/evidence.jsonl`

### Promotion-Gate Checkliste

- [ ] Experiment ist vollständig durchgeführt
- [ ] `CONTEXT.md` und `INITIAL.md` sind vorhanden und vollständig
- [ ] `evidence.jsonl` enthält mindestens einen maschinenlesbaren Eintrag
- [ ] `decision.yml` enthält `verdict: adopted`
- [ ] Manifest enthält `adoption_basis` (`executed` | `replicated` | `reconstructed`)
- [ ] Falls `execution_status ∈ {executed, replicated}`: `artifacts/<run-id>/run_meta.json` vorhanden und schema-valide; `test_output_file` existiert
- [ ] Schema- und Execution-Proof-Validierung bestanden (`make validate`)
- [ ] Katalogeintrag / Prompt / Combo liegt im korrekten Zielordner
- [ ] Frontmatter entspricht dem jeweiligen Schema (`catalog.entry.schema.json` / `combo.schema.json`)
- [ ] Keine manuellen Edits an generierten Artefakten

### Evidenz-Zusammenfassung
<!-- Kurze Zusammenfassung: Warum ist diese Praxis promotionswürdig? Belege aus evidence.jsonl. -->

### Aufwertungsbegründung

- **Grundlage:** <!-- Worauf stützt sich die Aufwertung? (Experiment, Evidenz, Replikation) -->
- **Unsicher bleibt:** <!-- Was bleibt offen, ungetestet oder kontextschmal? -->
- **Warum jetzt trotzdem:** <!-- Warum reicht die Grundlage für diesen Geltungssprung jetzt aus? -->
- **Alternative Lesart (optional):** <!-- Plausible alternative Deutung bei hoher Tragweite -->

### Reviewer-Hinweise
<!-- Besonderheiten, Einschränkungen, bekannte Limitationen -->
