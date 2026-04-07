# 🤖 Meta-Vibe-Coding: KI die Vibe-Coding optimiert

## Idee

Ein **Vibe-Advisor** – ein KI-System, das basierend auf Kontext (Projekttyp, Teamgröße, Deadline, Qualitätsanforderungen) den **optimalen Vibe-Coding-Stil** empfiehlt. Self-Improving durch Feedback.

## Konzept

### Vibe-Advisor Prompt

```
Du bist der Vibe-Advisor. Basierend auf den folgenden Informationen 
empfiehlst du den optimalen Vibe-Coding-Ansatz:

Input:
- Projekttyp: [z.B. REST-API, Frontend-App, CLI-Tool]
- Projektgröße: [klein/mittel/groß]
- Teamgröße: [solo/2-5/5+]
- Deadline: [heute/diese Woche/kein Druck]
- Qualitätsanforderung: [Prototyp/Produktion/Sicherheitskritisch]
- Erfahrungslevel mit dem Tech-Stack: [Anfänger/Fortgeschritten/Experte]
- Bestehende Codebase: [Greenfield/Brownfield]

Output:
- Empfohlener Stil + Begründung
- Empfohlene Techniken + Reihenfolge
- Empfohlenes Tool
- Warnungen und Hinweise
- Geschätzter Zeitaufwand
```

### Feedback-Loop

```
Nach dem Vibe-Coding:
"Der Vibe-Advisor empfahl [Ansatz]. 
Ergebnis: [was passiert ist]
Was würdest du beim nächsten Mal anders empfehlen?"
```

### Datenbank

Über Zeit sammelt sich eine Datenbank aus:
- Situation → Empfehlung → Ergebnis
- Daraus lernen: Welche Empfehlungen funktionieren in welchem Kontext?

## Status

💡 **Idee** – Vibe-Advisor-Prompt existiert als Konzept

## Nächste Schritte

- [ ] Vibe-Advisor-Prompt ausarbeiten und testen
- [ ] Erste 10 Situationen durchspielen
- [ ] Ergebnisse in Datenbank-Format erfassen
- [ ] Feedback-Loop implementieren
