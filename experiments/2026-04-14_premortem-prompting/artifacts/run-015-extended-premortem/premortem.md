# Extended Pre-Mortem (Run 015)

## Neue Fehlermuster (aus Run 014 + Analyse)

1. micro_price (zu kleine Preise nahe 0)
2. price=0 (Nullpreis)
3. extreme qty jenseits operativer Grenzen
4. nicht-listige `items`-Strukturen

## Regelergänzungen

- `price` muss numerisch und im Bereich `[0.01, 1_000_000]` liegen.
- `qty` muss int und im Bereich `[1, 1_000_000]` liegen.
- `items` muss nicht-leere Liste von Objekten sein.
