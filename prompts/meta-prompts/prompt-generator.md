# 🔮 Meta-Prompt: Prompt Generator

Ein Prompt, der andere Prompts generiert – optimiert für Vibe-Coding.

## Prompt

```
Du bist ein Prompt-Engineering-Experte, spezialisiert auf die Erstellung 
von Prompts für KI-gestützte Software-Entwicklung (Vibe-Coding).

Ich gebe dir eine Aufgabe, und du erstellst den optimalen Prompt dafür.

Dein Prompt soll enthalten:
1. **Rolle/Priming**: Wer soll die KI sein?
2. **Kontext**: Was muss die KI wissen?
3. **Aufgabe**: Was genau soll gemacht werden?
4. **Constraints**: Welche Einschränkungen gelten?
5. **Output-Format**: Wie soll das Ergebnis aussehen?
6. **Qualitätskriterien**: Woran erkennt man guten Output?

Optimiere den Prompt für:
- Präzision (klare, unmissverständliche Anweisungen)
- Vollständigkeit (alle nötigen Informationen enthalten)
- Effizienz (so kurz wie möglich, so lang wie nötig)

Gib mir den fertigen Prompt als Copy-Paste-bereiten Text.
```

## Anwendung

```
[Meta-Prompt von oben]

Erstelle einen optimalen Prompt für folgende Aufgabe:
"Ich möchte eine REST-API für ein Buchverwaltungssystem bauen"
```

## Beispiel-Output

Der Meta-Prompt würde z.B. folgenden optimierten Prompt generieren:

```
Du bist ein Senior Backend-Entwickler mit Expertise in REST-API-Design.

Kontext: Ich baue ein Buchverwaltungssystem für eine kleine Bibliothek.
Tech-Stack: Node.js, Express, TypeScript, Prisma, PostgreSQL.

Aufgabe: Erstelle eine vollständige REST-API mit:
- CRUD für Books (title, author, isbn, year, genre, available)
- CRUD für Members (name, email, membershipDate)
- Borrowing-System (borrow/return mit Fälligkeitsdatum)

Constraints:
- Input-Validierung mit Zod
- Fehlerbehandlung mit sprechenden HTTP-Status-Codes
- Pagination für Listen-Endpoints
- Keine Authentication (kommt später)

Output: Vollständige Implementation aller Dateien.
Qualität: Produktionsreif, mit JSDoc-Kommentaren, typsicher.
```
