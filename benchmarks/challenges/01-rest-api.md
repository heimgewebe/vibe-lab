# 🎮 Challenge 1: REST-API von Grund auf

## Beschreibung

Baue eine vollständige REST-API für ein **Aufgabenverwaltungssystem (Task Manager)** – von Null auf.

## Anforderungen

### Funktional
- CRUD-Operationen für Tasks (title, description, status, priority, dueDate)
- CRUD-Operationen für Projekte (name, description)
- Tasks gehören zu Projekten (1:N)
- Filtern von Tasks nach Status und Priorität
- Pagination für Listen-Endpoints

### Technisch
- Node.js oder Python
- Relationale Datenbank (PostgreSQL, SQLite)
- Input-Validierung
- Error Handling mit sinnvollen HTTP-Status-Codes
- Mindestens 5 Tests

### Nice-to-Have (optional)
- Authentication
- API-Dokumentation (Swagger/OpenAPI)
- Docker Setup

## Bewertungskriterien

| Kriterium | Gewicht |
|-----------|---------|
| Funktioniert alle CRUD-Operationen? | 30% |
| Codequalität und Struktur | 25% |
| Error Handling und Validierung | 20% |
| Tests vorhanden und sinnvoll? | 15% |
| Dokumentation | 10% |

## Zeitmessung

Stoppe die Zeit von der ersten Interaktion mit dem KI-Tool bis zur funktionierenden API.

## Ergebnis-Template

```yaml
challenge: rest-api
style: [verwendeter Stil]
techniques: [verwendete Techniken]
tool: [verwendetes Tool]
time_minutes: [Gesamtzeit]
iterations: [Anzahl Prompt-Iterationen]
result:
  crud_working: true/false
  code_quality: 1-5
  error_handling: 1-5
  tests: 1-5
  documentation: 1-5
notes: "..."
```
