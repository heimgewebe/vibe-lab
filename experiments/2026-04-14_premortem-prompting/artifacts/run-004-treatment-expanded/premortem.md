# Pre-Mortem (Run 004 Treatment Expanded)

## Risiken mit hoher Eintrittswahrscheinlichkeit

1. `price`/`qty` kommen als falsche Typen an (z. B. Strings).
2. Item-Felder fehlen partiell (`qty` oder `price`).
3. `email` fehlt oder ist ungültig.
4. Kaputtes JSON bricht den Ablauf vorzeitig.
5. DB-Fehler darf nicht als Erfolg maskiert werden.
6. Email-Fehler soll Legacy-kompatibel geschluckt werden.

## Checkliste

- [x] Typvalidierung für `price`/`qty`
- [x] Feldvalidierung je Item
- [x] Email-Pflichtfeld validiert
- [x] JSON-Decode Fehlerpfad
- [x] DB-Fehlerpfad -> `False`
- [x] Email-Fehlerpfad -> `True` (swallowed)
