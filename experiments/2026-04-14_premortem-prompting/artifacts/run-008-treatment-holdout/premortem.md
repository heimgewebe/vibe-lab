# Pre-Mortem (Run 008 Treatment Holdout)

## Antizipierte Failure-Pfade (vorab)

1. `email` fehlt.
2. `email` ungültiges Format.
3. `qty` fehlt.
4. `qty` falscher Typ.
5. `price` falscher Typ.
6. JSON ungültig.
7. DB-Write schlägt fehl.
8. Email-Service schlägt fehl (soll geschluckt werden).

> Holdout-Regel: `negative_price` und `zero_qty` wurden **nicht** explizit antizipiert.
