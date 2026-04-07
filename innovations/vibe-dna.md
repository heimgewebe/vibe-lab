# 🧬 Vibe-DNA: Kombinatorische Stilkarten

## Idee

Jeder Vibe-Coding-Stil wird als "Gen" mit definierten Eigenschaften modelliert. Stile können **kombiniert ("gekreuzt")** werden, um neue Hybrid-Stile zu erzeugen. Eine interaktive Matrix visualisiert, welche Kombinationen bereits getestet wurden.

## Konzept

### Gen-Eigenschaften

Jeder Stil hat eine "DNA" aus 7 Werten (1-5):

```
YOLO-Prompting:    [Speed:5, Accuracy:2, Quality:2, Iterate:2, CogLoad:4, Scale:1, Create:4]
Spec-First Vibe:   [Speed:3, Accuracy:4, Quality:4, Iterate:4, CogLoad:3, Scale:4, Create:2]
TDD-Vibe:          [Speed:2, Accuracy:5, Quality:5, Iterate:5, CogLoad:3, Scale:4, Create:2]
```

### Kreuzung

Wenn zwei Stile kombiniert werden, ergibt sich ein Hybrid:
```
YOLO + Spec-First = Guided YOLO
  → [Speed:4, Accuracy:3, Quality:3, Iterate:3, CogLoad:4, Scale:2, Create:4]
```

### Visualisierung

Eine Matrix aller möglichen Kombinationen:
```
             YOLO  Spec  TDD  Pair  FullAuto  Increm  Arch
YOLO          —     ✅    ❌    ⬜     ⬜       ⬜      ❌
Spec-First   ✅     —     ✅    ⬜     ⬜       ✅      ✅
TDD          ❌    ✅     —     ⬜     ❌       ✅      ⬜
...

✅ = Getestet + funktioniert
❌ = Getestet + funktioniert NICHT
⬜ = Noch nicht getestet
```

## Umsetzung

1. JSON-Datei mit allen Stil-DNAs
2. Script zum Berechnen von Hybrid-Werten
3. Markdown/HTML-Generierung der Matrix
4. Integration in die Website

## Status

💡 **Idee** – noch nicht implementiert

## Nächste Schritte

- [ ] DNA-Schema definieren
- [ ] Erste 8 Stile mit DNA versehen
- [ ] Kreuzungs-Algorithmus implementieren
- [ ] Matrix-Visualisierung erstellen
