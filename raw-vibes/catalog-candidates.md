# Katalog-Kandidaten

> **Achtung:** Dies sind ungeprüfte Kandidaten und Hypothesen. Sie stellen keine validierten Practices dar und dienen lediglich als Rohmaterial zur späteren experimentellen Validierung.

## Styles
- **YOLO Prompting**: Unstrukturiertes, direktes Prompting. Fokus auf maximaler Erstgeschwindigkeit.
- **Guided YOLO**: Leicht gesteuertes YOLO mit rudimentären Leitplanken, um kompletten Kontrollverlust zu vermeiden.
- **Spec-First Vibe**: Vorab-Spezifikation (oft iterativ mit dem LLM erstellt) dient als striktes Gerüst für die eigentliche Code-Generierung.
- **TDD Vibe**: Test-Driven Development im Vibe-Coding-Kontext. Das LLM schreibt erst die Tests, dann den Code.

## Techniques
- **Incremental Refinement**: Code wird nicht in einem Rutsch generiert, sondern durch viele kleine, gezielte Prompts iterativ verfeinert.
- **Pair Programming mit KI**: Der Mensch navigiert aktiv und trifft Architekturentscheidungen, die KI übernimmt ausschließlich die Tipp-Arbeit (Executant).

## Anti-Patterns
- **Context Window Overflow**: Zu viele Dateien oder zu langer Verlauf werden in den Prompt gestopft, das Modell verliert den Fokus oder vergisst Instruktionen.
- **Prompt Vagueness**: Zu ungenaue Anforderungen führen zu Annahmen des Modells, die oft falsch sind und massives Rework nach sich ziehen.
- **Copy-Paste Blindness**: Generierter Code wird unkritisch übernommen, wodurch subtile Fehler (z.B. in der Geschäftslogik) unentdeckt bleiben.
