# Pre-Mortem (Run 006 Treatment Variant B)

## Antizipierte Failure-Pfade

1. `email` fehlt.
2. `email` hat kein valides Format.
3. `qty` fehlt.
4. `qty` hat falschen Typ.
5. `price` hat falschen Typ.
6. JSON ist ungültig.
7. DB-Write schlägt fehl.
8. Email-Service schlägt fehl (soll geschluckt werden).

## Checkliste

- [x] Email-Pflicht + rudimentäres Format validieren
- [x] `price`/`qty` Feld- und Typvalidierung
- [x] JSON-Fehlerpfad
- [x] DB-Fehlerpfad = `False`
- [x] Email-Fehlerpfad = `True`
