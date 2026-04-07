# 📊 Bewertungskatalog

Jeder Vibe-Coding-Ansatz wird entlang standardisierter Dimensionen bewertet. Dies ermöglicht vergleichbare Einschätzungen und datengetriebene Entscheidungen.

## Bewertungsdimensionen

### ⏱️ Geschwindigkeit

**Frage**: Wie schnell gelangt man von der Idee zum funktionierenden Code?

| Score | Bedeutung |
|:-----:|-----------|
| 1 | Langsamer als manuelles Coding |
| 2 | Ähnlich schnell wie manuelles Coding |
| 3 | Merklich schneller (ca. 2x) |
| 4 | Deutlich schneller (ca. 3-5x) |
| 5 | Extrem schnell (>5x), nahezu instant |

### 🎯 Treffsicherheit

**Frage**: Wie oft liefert der erste Versuch das gewünschte Ergebnis?

| Score | Bedeutung |
|:-----:|-----------|
| 1 | Fast nie (<20% korrekt beim ersten Mal) |
| 2 | Selten (20-40%) |
| 3 | Manchmal (40-60%) |
| 4 | Meistens (60-80%) |
| 5 | Fast immer (>80%) |

### 🏗️ Codequalität

**Frage**: Wie gut ist der generierte Code in Bezug auf Wartbarkeit, Lesbarkeit und Testabdeckung?

| Score | Bedeutung |
|:-----:|-----------|
| 1 | Kaum wartbar, schwer lesbar, keine Tests |
| 2 | Grundlegend funktional, aber chaotisch |
| 3 | Akzeptable Qualität, einige Best Practices |
| 4 | Gute Qualität, saubere Struktur, einige Tests |
| 5 | Produktionsreif, gut getestet, vorbildlich |

### 🔄 Iterationsfähigkeit

**Frage**: Wie gut lässt sich der Output weiterentwickeln und verfeinern?

| Score | Bedeutung |
|:-----:|-----------|
| 1 | Jede Änderung erfordert komplett neuen Anlauf |
| 2 | Große Änderungen sind schwierig |
| 3 | Änderungen möglich, aber aufwändig |
| 4 | Gut iterierbar, Feedback wird verstanden |
| 5 | Exzellent – kleine Prompts führen zu präzisen Anpassungen |

### 🧠 Kognitive Last

**Frage**: Wie viel muss der Mensch noch denken, korrigieren und kontrollieren?

| Score | Bedeutung |
|:-----:|-----------|
| 1 | Mehr Aufwand als manuelles Coding |
| 2 | Hohe kognitive Last, viel Kontrolle nötig |
| 3 | Moderate Last, gelegentliche Korrekturen |
| 4 | Geringe Last, meist Überprüfung reicht |
| 5 | Minimal – man kann sich auf die Vibe konzentrieren |

### 📐 Skalierbarkeit

**Frage**: Funktioniert der Ansatz auch bei größeren, komplexeren Projekten?

| Score | Bedeutung |
|:-----:|-----------|
| 1 | Nur für triviale Aufgaben (<50 Zeilen) |
| 2 | Für kleine Aufgaben (einzelne Funktionen) |
| 3 | Für mittlere Aufgaben (Module, Features) |
| 4 | Für große Aufgaben (ganze Services) |
| 5 | Für komplexe Projekte (Multi-Service-Architekturen) |

### 🎨 Kreativität

**Frage**: Liefert der Ansatz innovative, überraschend gute Lösungen?

| Score | Bedeutung |
|:-----:|-----------|
| 1 | Nur Standardlösungen, keine Kreativität |
| 2 | Gelegentlich leicht kreative Ansätze |
| 3 | Regelmäßig gute, teilweise überraschende Ideen |
| 4 | Oft kreative, innovative Lösungen |
| 5 | Konsistent kreativ, liefert Lösungen, die man selbst nicht bedacht hätte |

## Gesamtbewertung

Die Gesamtbewertung ist **kein** einfacher Durchschnitt. Je nach Kontext haben unterschiedliche Dimensionen unterschiedliches Gewicht:

| Kontext | Wichtigste Dimensionen |
|---------|----------------------|
| Prototyping / MVP | Geschwindigkeit, Kreativität |
| Produktionscode | Codequalität, Skalierbarkeit |
| Lernen / Exploration | Kreativität, Kognitive Last |
| Refactoring | Iterationsfähigkeit, Codequalität |
| Deadline-Druck | Geschwindigkeit, Treffsicherheit |

## Tipps für Bewerter

1. **Sei ehrlich** – Überbewertung hilft niemandem
2. **Vergleiche mit Baseline** – Wie wäre das Ergebnis OHNE diesen Ansatz?
3. **Dokumentiere Kontext** – Erfahrungslevel, Projektgröße, Aufgabentyp
4. **Wiederhole** – Ein einzelner Datenpunkt ist keine Bewertung
5. **Aktualisiere** – Tools und Modelle ändern sich, Bewertungen auch
