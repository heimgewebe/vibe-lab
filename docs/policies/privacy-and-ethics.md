---
title: "Privacy- und Ethik-Policy"
status: active
canonicality: operative
---

# Privacy- und Ethik-Policy

## Grundsatz

Personenbezogene Daten und Secrets sind in allen Repository-Artefakten untersagt.

## Regeln

1. **Keine personenbezogenen Daten** in `evidence.jsonl`, Experiment-Artefakten oder Exports.
2. **Keine Secrets** (API-Keys, Tokens, Passwörter) in irgendeinem committed Artefakt.
3. **Lokale Konfiguration** gehört in `.env` (nicht committed). `.env.example` zeigt nur die Struktur.
4. **Push Protection** und **Secret Scanning** sollen auf Repository-Ebene aktiviert sein.
5. **Prompt-Injection-Härtung:** Exporte durchlaufen ein striktes Sanitization-Prinzip.

## Verantwortlichkeit

Jeder Contributor ist dafür verantwortlich, dass seine Beiträge diese Policy einhalten. Reviewer prüfen dies im Promotion-Gate.
