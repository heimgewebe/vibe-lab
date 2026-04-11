# Ergebnisse: YOLO vs. Spec-First

Basierend auf den gesammelten qualitativen Beobachtungen ergeben sich folgende Befunde:

## YOLO (You Only Look Once)
- **Geschwindigkeit (initial)**: Sehr hoch. Die Barriere zur ersten lauffähigen Code-Version ist minimal.
- **Nacharbeit (Rework)**: Sehr hoch. Der Code ist oft nicht passgenau und erfordert manuelle Korrekturen, die teilweise den Zeitvorteil zunichte machen.
- **Iterierbarkeit**: Niedrig. Ohne zugrundeliegende Struktur wird es schwer, das System nachträglich sauber zu erweitern.

## Spec-First
- **Geschwindigkeit (initial)**: Niedrig bis mittel. Das Verfassen der Spezifikation kostet spürbar Zeit.
- **Nacharbeit (Rework)**: Niedrig. Der erzeugte Code ist signifikant näher an der Zielarchitektur.
- **Iterierbarkeit**: Sehr hoch. Die Struktur erzwingt modularere Ergebnisse und das Modell verliert seltener den Kontext.

## Fazit
Der Trade-off ist klar: **YOLO tauscht Qualität und Iterierbarkeit gegen initiale Geschwindigkeit.** Spec-First erzwingt eine Verlangsamung am Anfang, um Rework am Ende zu verhindern. Wo harte Daten/quantitative Benchmarks für exakte Metriken fehlen, markieren diese Beobachtungen eine epistemische Leerstelle, die in zukünftigen, spezifischeren Experimenten (z.B. auf Basis der neuen Benchmarks) quantifiziert werden muss.
