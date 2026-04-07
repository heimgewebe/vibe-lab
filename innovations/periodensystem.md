# 🧩 Vibe-Coding-Periodensystem

## Idee

Eine visuelle Darstellung aller bekannten Vibe-Coding-Techniken als **interaktives Periodensystem** – gruppiert nach Kategorien und Eigenschaften, wie echte chemische Elemente.

## Konzept

### Element-Struktur

Jedes "Element" hat:
- **Symbol**: 2-3 Buchstaben (z.B. "Yo" für YOLO, "Sp" für Spec-First)
- **Ordnungszahl**: Reihenfolge der Entdeckung/Dokumentation
- **Gruppe**: Kategorie (Stile, Techniken, Workflows, Anti-Patterns)
- **Periode**: Komplexitätslevel
- **Masse**: Bewertungsscore (Gesamtqualität)

### Gruppen (Spalten)

```
Gruppe 1: Stile           (🎨 farbig: blau)
Gruppe 2: Techniken       (🔧 farbig: grün)
Gruppe 3: Workflows       (📋 farbig: orange)
Gruppe 4: Anti-Patterns   (⚠️ farbig: rot)
Gruppe 5: Tools           (💻 farbig: lila)
```

### Perioden (Zeilen)

```
Periode 1: Beginner-Level (YOLO, Prompt Priming, ...)
Periode 2: Intermediate   (Guided YOLO, Chain-of-Thought, ...)
Periode 3: Advanced       (Spec-First, TDD-Vibe, Architecture-First, ...)
Periode 4: Expert         (Meta-Vibe-Coding, Vibe-DNA, ...)
```

### Interaktivität

- Hover: Kurzbeschreibung
- Klick: Detailseite mit vollem Katalog-Eintrag
- Filter: Nach Gruppe, Periode, Tool-Kompatibilität
- Kombination: Zwei Elemente auswählen → Combo-Rezept anzeigen

## Umsetzung

- JSON-Datei mit allen Elementen und Positionen
- React/Svelte-Komponente für die Darstellung
- Integration in die VitePress/Astro-Website

## Status

💡 **Idee** – Konzeptphase

## Nächste Schritte

- [ ] Alle bestehenden Einträge als "Elemente" definieren
- [ ] Layout des Periodensystems entwerfen
- [ ] JSON-Schema für Elemente erstellen
- [ ] Interaktive Komponente implementieren
