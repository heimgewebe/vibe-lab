# Methode: YOLO vs. Spec-First

Dieses Experiment vergleicht zwei gegensätzliche Vibe-Coding-Ansätze:

## 1. Arm A: Der "YOLO"-Ansatz (You Only Look Once)
Hierbei wird dem Agenten oder dem Modell ein sehr breiter, meist kurzer Prompt gegeben, der direkt zur Code-Generierung aufruft.
- **Fokus**: Schnelle Erstgenerierung.
- **Steuerung**: Minimal, keine Vorab-Spezifikation.
- **Korrekturschleifen**: Finden erst nach der Generierung statt, oft reaktiv auf Fehler.

## 2. Arm B: Der "Spec-First"-Ansatz
Dieser Ansatz trennt die Planung strikt von der Generierung. Es wird im Vorfeld eine formale Spezifikation (z.B. Markdown, Pseudocode, oder Test Cases) erstellt, die dann dem Agenten als strenge Vorgabe dient.
- **Fokus**: Struktur und Präzision.
- **Steuerung**: Maximal durch vorherige Definition des "Was".
- **Korrekturschleifen**: Fehler werden präventiv in der Spec abgefangen, Generierungsschleifen reduzieren sich.

## Durchführung
Beide Ansätze wurden in der Altversion des Vibe-Labs qualitativ an mehreren Use-Cases erprobt. Dieses Experiment synthetisiert die qualitativen Beobachtungen zu den Metriken Geschwindigkeit (Speed), Nacharbeit (Rework/Qualität) und Iterierbarkeit (Struktur).
