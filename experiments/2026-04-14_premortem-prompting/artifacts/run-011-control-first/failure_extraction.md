# Failure Extraction (Run 011)

Aus `test_injection.py` beobachtete Fails:
- missing_email_rejected
- negative_price_rejected
- zero_qty_rejected
- extreme_qty_rejected

Abgeleitete Regeln für Folge-Pre-Mortem:
1. email Pflichtfeld
2. price > 0
3. qty > 0 und integer
4. qty obere Schranke gegen Extremwerte
