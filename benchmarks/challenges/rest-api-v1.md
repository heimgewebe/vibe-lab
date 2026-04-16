---
title: "REST-API CRUD Challenge v1"
status: active
canonicality: operative
document_role: report
---

# Benchmark Challenge: REST-API CRUD (v1)

## Zweck

Standardisierte Vergleichsaufgabe zur Bewertung von Vibe-Coding-Techniken bei der Generierung von REST-APIs.

## Aufgabe

Generiere eine REST-API mit den folgenden Anforderungen:

### Endpunkte
1. `POST /users` — Benutzer erstellen
2. `GET /users/:id` — Benutzer abrufen
3. `PUT /users/:id` — Benutzer aktualisieren
4. `DELETE /users/:id` — Benutzer löschen
5. `GET /users` — Benutzerliste mit Pagination

### Anforderungen
- TypeScript / Node.js (Express.js oder Fastify)
- Input-Validierung für alle Endpunkte
- Konsistente Response-Struktur (Envelope-Pattern)
- Korrekte HTTP-Statuscodes (200, 201, 400, 404, 409, 422, 500)
- Pagination mit `page` und `limit` Query-Parametern

## Bewertungskriterien

| Kriterium          | Gewicht | Beschreibung                                  |
| ------------------ | ------: | --------------------------------------------- |
| Vollständigkeit    | 30%     | Alle Endpunkte und Fehlercodes vorhanden       |
| Validierung        | 20%     | Input-Validierung korrekt implementiert         |
| Konsistenz         | 20%     | Einheitliche Response-Strukturen                |
| Code-Qualität      | 15%     | Lesbarkeit, Typisierung, Struktur              |
| Nacharbeit         | 15%     | Zeilen manueller Korrektur nach Generierung     |

## Versionierung

- **Version:** v1
- **Erstellt:** 2026-04-10
- **Änderungen:** Initiale Version

> Beim Referenzieren in `decision.yml` bitte `challenge_version: "rest-api-v1"` angeben.
