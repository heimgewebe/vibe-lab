# Katalog-Kandidaten

> **Achtung:** Dies sind ungeprüfte Kandidaten und Hypothesen. Sie stellen keine validierten Practices dar und dienen lediglich als Rohmaterial zur späteren experimentellen Validierung.

## Styles
- **YOLO Prompting**: Die Annahme, dass unstrukturiertes, direktes Prompting zu maximaler Erstgeschwindigkeit führt.
- **Guided YOLO**: Die Idee, ein leicht gesteuertes YOLO mit rudimentären Leitplanken zu versehen, um kompletten Kontrollverlust zu vermeiden.
- **Spec-First Vibe**: Die Hypothese, dass eine Vorab-Spezifikation als striktes Gerüst für die Code-Generierung dient und Nacharbeit minimiert.
- **TDD Vibe**: Test-Driven Development im Vibe-Coding-Kontext erproben: Das LLM schreibt erst die Tests, dann den Code.

## Techniques
- **Incremental Refinement**: Code nicht in einem Rutsch generieren, sondern durch viele kleine, gezielte Prompts iterativ verfeinern.
- **Pair Programming mit KI**: Ein möglicher Workflow, bei dem der Mensch aktiv navigiert und Architekturentscheidungen trifft, während die KI ausschließlich tippt.

## Anti-Patterns
- **Context Window Overflow**: Die Vermutung, dass zu viele Dateien oder ein zu langer Verlauf im Prompt dazu führen, dass das Modell Anweisungen vergisst.
- **Prompt Vagueness**: Zu ungenaue Anforderungen, die vermutlich zu falschen Annahmen des Modells und massivem Rework führen.
- **Copy-Paste Blindness**: Das unkritische Übernehmen von generiertem Code, wodurch subtile Fehler unentdeckt bleiben könnten.
