---
title: "Failure Modes: Upfront Structuring"
status: adopted
canonicality: operative
---

# failure_modes.md — Fehler & Grenzen

## Übersicht bekannter Failure Modes

### Spec-Ignorance
- **Beschreibung:** Das Modell generiert zwar eine perfekte Spezifikation (oder perfekte Tests), ignoriert diese aber teilweise bei der sofort darauffolgenden Code-Generierung im selben Prompt.
- **Auslöser:** Kontext-Fenster-Überlastung oder starke interne Biasse des Modells für bestimmte Standard-Implementierungen.
- **Mitigation:** Trennung in zwei physische Prompt-Schritte (erst Spec generieren und bestätigen, dann Code basierend auf der Spec anfordern).

### Over-Specification
- **Beschreibung:** Das Modell verliert sich in der Spezifikation von theoretischen, irrelevanten Edge-Cases (z.B. römische Zahlen über 10 Millionen), was die Implementierung unnötig komplex macht.
- **Auslöser:** Zu offene Prompts bei der Spec-Generierung.
- **Mitigation:** Klare Constraints setzen ("Fokussiere dich auf Standard-Römische-Zahlen bis 3999").
