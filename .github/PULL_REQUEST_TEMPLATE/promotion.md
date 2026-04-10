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
- [ ] Schema-Validierung bestanden (`make validate`)
- [ ] Katalogeintrag / Prompt / Combo liegt im korrekten Zielordner
- [ ] Frontmatter entspricht dem jeweiligen Schema (`catalog.entry.schema.json` / `combo.schema.json`)
- [ ] Keine manuellen Edits an generierten Artefakten

### Evidenz-Zusammenfassung
<!-- Kurze Zusammenfassung: Warum ist diese Praxis promotionswürdig? Belege aus evidence.jsonl. -->

### Reviewer-Hinweise
<!-- Besonderheiten, Einschränkungen, bekannte Limitationen -->
