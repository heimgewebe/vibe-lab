---
title: "Spec-First API Prompt"
status: adopted
canonicality: operative
relations:
  - type: derived_from
    target: ../../catalog/techniques/spec-first-prompting.md
  - type: validated_by
    target: ../../experiments/2026-04-08_spec-first/results/result.md
document_role: unknown
---

# Spec-First API Prompt

> Adoptierter Prompt für den Spec-First-Ansatz bei REST-API-Generierung.

## Prompt (Schritt 1 — Spezifikation)

```
Erstelle eine OpenAPI 3.0 Spezifikation für folgende API:

[AUFGABENBESCHREIBUNG]

Die Spezifikation muss enthalten:
- Alle Endpunkte mit Pfaden, Methoden und Beschreibungen
- Request-Body-Schemas für POST/PUT
- Response-Schemas für alle Endpunkte (inkl. Fehlerfälle)
- HTTP-Statuscodes: 200, 201, 400, 404, 409, 422, 500
- Query-Parameter für Pagination (page, limit) bei Listen-Endpunkten
- Validierungsregeln (required, minLength, format etc.)

Gib die vollständige Spec im YAML-Format aus.
```

## Prompt (Schritt 2 — Implementierung)

```
Implementiere diese OpenAPI-Spezifikation als Express.js/TypeScript API.
Halte dich exakt an die definierten Schemas und Statuscodes.
Nutze ein einheitliches Response-Envelope-Pattern.
```

## Hinweise

- Zwischen Schritt 1 und 2: Spec reviewen und ggf. anpassen
- Bei Abweichungen: Zuerst die Spec korrigieren, dann neu generieren
- Funktioniert am besten bei mittlerer bis hoher Komplexität (>1 Entity)

## Herkunft

Validiert durch: [Experiment 2026-04-08 Spec-First](../../experiments/2026-04-08_spec-first/)
