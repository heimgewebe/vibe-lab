Änderungsübersicht

Geändert:
- In der Zielstruktur auf Root-Ebene wurde das `Makefile` explizit ergänzt, mit dem Kommentar: `# Schlanke Routine-Frontdoor (z.B. make validate, make vibe)`.
- Der Kommentar bei `tools/vibe-cli/` in der Zielstruktur wurde leicht präzisiert zu `# Scaffolding-CLI (spezifische Kommandos)`, um die Trennung zum Makefile deutlich zu machen.
- Im Text unter Phase A wurde bei "Scaffolding-CLI (Make-Frontdoor)" deutlicher herausgestellt: "Ein zentrales `Makefile` dient als schlanke Routine-Frontdoor (z.B. `make validate`, `make vibe`), während ein dediziertes CLI (`tools/vibe-cli`) spezifische Scaffolding-Befehle... bereitstellt".
- Im Changelog wurde der Kohärenzfix bezüglich der Make-Frontdoor am Ende ergänzt.

Nicht verändert:
- Es wurden keine neuen Phasen, Artefaktklassen, Sicherheits- oder Governance-Modelle eingeführt.
- Es wurden keine zusätzlichen Generatoren ergänzt.
- Keine weiteren bestehenden Konzepte (wie Epistemische Zustände, Intelligence Layer, Zonenmodell) wurden angerührt oder sprachlich umgebaut.
