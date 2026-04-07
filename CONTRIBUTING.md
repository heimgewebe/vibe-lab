# 🤝 Contributing to Vibe-Lab

Danke, dass du zu Vibe-Lab beitragen möchtest! Hier erfährst du, wie du mitmachen kannst.

## 📋 Beitragsarten

### 📝 Neuen Katalog-Eintrag erstellen

1. Wähle die passende Kategorie: `styles/`, `technologies/`, `techniques/`, `workflows/` oder `anti-patterns/`
2. Erstelle eine neue Markdown-Datei mit YAML-Frontmatter (siehe [Schema](schemas/))
3. Verwende den Dateinamen im Format: `kebab-case-name.md`
4. Fülle alle Pflichtfelder im Frontmatter aus
5. Erstelle einen Pull Request

### 🧪 Experiment dokumentieren

1. Kopiere `experiments/_template/` als `experiments/YYYY-MM-DD_experiment-name/`
2. Fülle die `README.md` im Experiment-Ordner aus
3. Dokumentiere alle Artefakte (Prompts, Code, Screenshots)
4. Erstelle einen Pull Request

### 🔀 Combo-Rezept teilen

1. Erstelle eine neue Datei in `combos/`
2. Beschreibe die Kombination aus Stil + Technik + Tool
3. Dokumentiere deine Erfahrung und Bewertung

### 💡 Innovation vorschlagen

1. Erstelle eine neue Datei in `innovations/`
2. Beschreibe die Idee, den erwarteten Nutzen und mögliche Umsetzung

### 🎯 Prompt teilen

1. Wähle die passende Kategorie: `system-prompts/`, `meta-prompts/` oder `chain-templates/`
2. Dokumentiere den Prompt mit Kontext und Anwendungsbeispielen

## ✅ Qualitätskriterien

### Katalog-Einträge

- [ ] YAML-Frontmatter mit allen Pflichtfeldern
- [ ] Klare, verständliche Beschreibung
- [ ] Mindestens ein konkretes Beispiel
- [ ] Bewertung anhand der Standard-Dimensionen
- [ ] Synergien und Anti-Synergien identifiziert
- [ ] Tags korrekt vergeben

### Experimente

- [ ] Klare Hypothese formuliert
- [ ] Setup vollständig dokumentiert
- [ ] Durchführung nachvollziehbar beschrieben
- [ ] Artefakte beigefügt
- [ ] Ergebnis quantitativ und qualitativ bewertet
- [ ] Learnings herausgearbeitet

## 🏷️ Labels

Wir verwenden folgende Labels für Issues und PRs:

| Label | Beschreibung |
|-------|-------------|
| `style` | Neuer oder aktualisierter Vibe-Coding-Stil |
| `technique` | Neue oder aktualisierte Technik |
| `tool` | Neues oder aktualisiertes Tool/Technologie |
| `experiment` | Neues Experiment |
| `combo` | Neues Kombinationsrezept |
| `innovation` | Neue Idee/Innovation |
| `prompt` | Neuer Prompt |
| `needs-testing` | Eintrag muss noch getestet werden |
| `bug` | Fehler in bestehendem Eintrag |
| `documentation` | Verbesserung der Dokumentation |

## 📐 Formatierung

- **Sprache**: Deutsch oder Englisch (Deutsch bevorzugt für Beschreibungen)
- **Dateinamen**: `kebab-case.md`
- **Frontmatter**: YAML, validiert gegen Schema in `schemas/`
- **Markdown**: Standard GitHub Flavored Markdown
- **Emojis**: Sparsam und konsistent einsetzen

## 🔄 Pull Request Prozess

1. Fork das Repository
2. Erstelle einen Feature-Branch: `git checkout -b feature/mein-beitrag`
3. Mache deine Änderungen
4. Stelle sicher, dass das Frontmatter dem Schema entspricht
5. Erstelle einen Pull Request mit aussagekräftiger Beschreibung
6. Warte auf Review und arbeite Feedback ein

## 💬 Diskussionen

Nutze GitHub Discussions für:
- Fragen zu Vibe-Coding-Stilen
- Erfahrungsberichte
- Ideen-Brainstorming
- Community-Austausch

---

*Jeder Beitrag macht Vibe-Lab besser. Danke fürs Mitmachen!* 🙏
