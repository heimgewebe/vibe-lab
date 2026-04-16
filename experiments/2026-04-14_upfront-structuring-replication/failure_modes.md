---
title: "Failure Modes: Upfront Structuring Replication"
status: testing
canonicality: operative
document_role: experiment
---

# failure_modes.md — Fehler & Grenzen

## Übersicht bekannter Failure Modes

### Spec-Ignorance
- **Beschreibung:** Das Modell generiert zwar eine perfekte Spezifikation (oder perfekte Tests), ignoriert diese aber teilweise bei der sofort darauffolgenden Code-Generierung im selben Prompt.
- **Auslöser:** Kontext-Fenster-Überlastung oder starke interne Biasse des Modells.
- **Mitigation:** Trennung in zwei physische Prompt-Schritte.
