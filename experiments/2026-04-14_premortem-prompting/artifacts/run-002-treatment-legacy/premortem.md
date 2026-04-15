# Pre-Mortem (Run 002 Treatment)

## Erwartbare Failure Modes vor Implementierung

1. **Ungültiges JSON wird nicht sauber behandelt**
   - Trigger: kaputtes JSON im Input
   - Symptom: ungefangene Exception
   - Mitigation: explizites `json.JSONDecodeError`-Handling

2. **Leere `items` werden nicht als Fehler gewertet**
   - Trigger: `items: []`
   - Symptom: Auftrag wird trotzdem verarbeitet
   - Mitigation: Validator mit klarer `ValueError`

3. **E-Mail-Fehler brechen Gesamtablauf**
   - Trigger: SMTP/Email-Service nicht verfügbar
   - Symptom: `process_order` liefert fälschlich `False`
   - Mitigation: E-Mail-Fehler isoliert fangen, Hauptablauf erfolgreich lassen

4. **Berechnung des Totals fehlerhaft bei mehreren Positionen**
   - Trigger: mehrere Items mit qty/price
   - Symptom: falscher Gesamtbetrag
   - Mitigation: dedizierte `OrderCalculator`-Klasse + Unit-Test

5. **Monolith verhindert gezieltes Testen**
   - Trigger: Geschäftslogik und I/O in einer Methode
   - Symptom: aufwändige/intransparente Tests
   - Mitigation: Entkopplung in Validator, Calculator, Processor

## Abgeleitete Checkliste

- [x] JSON-Parse-Fehler explizit behandelt
- [x] Leere `items` validiert
- [x] E-Mail-Fehler isoliert (Legacy-Verhalten bleibt)
- [x] Total-Berechnung über dedizierte Klasse
- [x] Komponenten testbar per Dependency Injection
