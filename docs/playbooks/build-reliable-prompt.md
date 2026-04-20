---
title: "Playbook: Build a Reliable Prompt"
status: active
canonicality: operative
created: "2026-04-20"
updated: "2026-04-20"
relations:
  - type: references
    target: ../../catalog/techniques/spec-first-prompting.md
  - type: references
    target: ../../catalog/techniques/prompt-length-control.md
  - type: references
    target: ../../catalog/anti-patterns/vague-prompt-and-fix.md
  - type: references
    target: ../../catalog/anti-patterns/token-bloat-as-quality-proxy.md
---

# Playbook: Build a Reliable Prompt

> Von Problem zu validiertem, wiederverwendbarem Prompt — Schritt für Schritt.

## Zielgruppe

Entwickler, die einen LLM-Prompt für eine wiederkehrende Aufgabe bauen wollen, der **nachweislich** funktioniert — nicht nur beim ersten Versuch gut aussieht.

## Pipeline-Übersicht

```
Problem → Technique → Combo → Prompt → Validation
```

## Schritt 1: Problem klar definieren

**Ziel:** Verstehen, was der Prompt leisten muss.

- [ ] Aufgabe in einem Satz beschreiben
- [ ] Input/Output-Format definieren (was geht rein, was kommt raus?)
- [ ] Bekannte Edge Cases sammeln
- [ ] Erfolg messbar machen (woran erkenne ich, dass der Prompt funktioniert?)

**Anti-Pattern vermeiden:** [Vague-Prompt-and-Fix](../../catalog/anti-patterns/vague-prompt-and-fix.md) — nicht einfach loslegen und iterativ nachbessern.

## Schritt 2: Passende Technique auswählen

**Ziel:** Den richtigen Prompting-Ansatz für die Aufgabe identifizieren.

Frage dich:
- Braucht die Aufgabe **formale Struktur** (API, Schema, Interface)?
  → [Spec-First Prompting](../../catalog/techniques/spec-first-prompting.md)
- Braucht die Aufgabe **explizite Constraints** (Validierung, Edge Cases)?
  → [Constraint-Before-Code](../../instruction-blocks/constraint-before-code.md)
- Gibt es eine **alternative Erklärung**, warum dein Ansatz funktioniert?
  → [Prompt-Length Control](../../catalog/techniques/prompt-length-control.md) (Stichwort: Token-Volumen ≠ Qualität)

**Anti-Pattern vermeiden:** [Token-Bloat-as-Quality-Proxy](../../catalog/anti-patterns/token-bloat-as-quality-proxy.md) — mehr Text ≠ besserer Code.

## Schritt 3: Techniques kombinieren (Combo prüfen)

**Ziel:** Synergien zwischen Techniques nutzen.

Prüfe im [Combos-Katalog](../../catalog/combos/), ob eine bewährte Kombination existiert:
- [Spec-First + Constraint-Control](../../catalog/combos/spec-first-constraint-control.md)
- [Spec-First + Anti-Pattern-Awareness](../../catalog/combos/spec-first-anti-pattern-awareness.md)

**Prinzip:** Eine Combo ist mehr als die Summe ihrer Teile — die Techniques verstärken sich gegenseitig.

## Schritt 4: Prompt bauen

**Ziel:** Einen konkreten, wiederverwendbaren Prompt formulieren.

Nutze die Instruction-Blocks als Bausteine:

1. **Eröffnung:** [Spec-First](../../instruction-blocks/spec-first.md) — Spezifikation vor Code
2. **Constraints:** [Constraint-Before-Code](../../instruction-blocks/constraint-before-code.md) — Alle Einschränkungen explizit
3. **Edge Cases:** [Edge-Case-Enumeration](../../instruction-blocks/edge-case-enumeration.md) — Grenzfälle benennen
4. **Validierung:** [Validate-Against-Spec](../../instruction-blocks/validate-against-spec.md) — Output gegen Spec prüfen

**Struktur eines guten Prompts:**

```
[Aufgabenbeschreibung — 1 Satz]

Bevor du implementierst:
1. [Constraint-Block: Input/Output/Fehler definieren]
2. [Spezifikation: Formales Format wählen]

Dann:
3. [Implementierung nach Spezifikation]

Danach:
4. [Validierung gegen die Spezifikation]
```

## Schritt 5: Prompt validieren

**Ziel:** Sicherstellen, dass der Prompt reproduzierbar funktioniert.

- [ ] Prompt an mindestens 2 verschiedenen Aufgaben testen
- [ ] Ergebnis gegen die Constraints aus Schritt 1 prüfen
- [ ] Edge Cases durchspielen
- [ ] Ergebnis dokumentieren (evidence.jsonl-Format)

**Wenn der Prompt nicht funktioniert:**
- Constraints zu vage? → Schritt 2 wiederholen (Constraint-Before-Code)
- Falsche Technique? → Schritt 2 mit anderem Ansatz
- Spec nicht eingehalten? → Validate-Against-Spec-Block verstärken

## Schritt 6: Prompt adoptieren (optional)

**Ziel:** Erfolgreichen Prompt in die Bibliothek aufnehmen.

Wenn der Prompt bei mindestens 2 Aufgaben nachweislich funktioniert:

1. Als `prompts/adopted/<name>.md` ablegen
2. Technique-Eintrag in `catalog/techniques/` erstellen oder referenzieren
3. Instruction-Blocks extrahieren (portierbare Bausteine)
4. Anti-Pattern dokumentieren (was funktioniert **nicht**?)
5. `make validate` und `make generate` ausführen

## Checkliste (Kurzform)

- [ ] Problem in einem Satz definiert
- [ ] Input/Output/Edge Cases dokumentiert
- [ ] Passende Technique gewählt (nicht bloß „viel Text")
- [ ] Combo geprüft (Synergien nutzen)
- [ ] Prompt mit Instruction-Blocks gebaut
- [ ] An mindestens 2 Aufgaben getestet
- [ ] Ergebnis dokumentiert
- [ ] Anti-Patterns vermieden (Vague-Prompt, Token-Bloat)
