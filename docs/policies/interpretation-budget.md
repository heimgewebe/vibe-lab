---
title: "Interpretation Budget"
status: active
canonicality: operative
---

# Interpretation Budget

## Zweck

Das Interpretation Budget verhindert Overclaiming: Es erzwingt eine explizite Trennung zwischen *was beobachtet wurde* und *was daraus gefolgert werden darf*.

Ein Experiment erzeugt Daten. Diese Daten erlauben bestimmte Schlüsse — und schließen andere aus. Ohne explizite Grenzziehung wandern Befunde stillen schritts von „unter diesen Bedingungen beobachtet" zu „generell wahr". Dieser Validator unterbricht diesen Drift an der einzig sinnvollen Stelle: beim Übergang zur Promotion.

**Pflicht:** Jedes Experiment mit `status: adopted` muss einen ausgefüllten `## Interpretation Budget` Block in `results/result.md` haben, bevor es in `catalog/` oder `prompts/` promotet werden darf.

## Wann ist der Block Pflicht?

| Experiment-Status | Pflicht? |
|---|---|
| `adopted` | ✅ Ja — CI-Gate, Promotion gesperrt ohne Block |
| `testing` | Nein — optional, empfohlen |
| `inconclusive` | Nein |
| `designed` | Nein |
| `rejected` | Nein |

## Struktur des Blocks

```markdown
## Interpretation Budget

### Allowed Claims
- Was darf aus diesem Experiment direkt gefolgert werden?

### Disallowed Claims
- Was darf NICHT gefolgert werden? Grenzen, Übertragbarkeits-Einschränkungen.

### Evidence Basis
- Direkt beobachtet:
- Indirekt gestützt:
- Nicht getestet:
```

**Mindestanforderung:** Mind. 1 konkreter (nicht-Platzhalter) Eintrag in `Allowed Claims` und `Disallowed Claims`.

## Beispiele

### ✅ Gut: Präzise Grenzziehung

```markdown
### Allowed Claims
- Spec-First reduziert Nacharbeit bei REST-API-Tasks (3 Tasks, GPT-4, 1 Person, Faktor 5–6×).

### Disallowed Claims
- Spec-First ist generell überlegen — zu klein für generelle Aussagen.
- Das Ergebnis überträgt sich auf andere LLMs oder Domänen.
```

**Warum gut:** Erlaubter Claim ist konkret und belegt (Task-Anzahl, Modell, Messung). Verbotener Claim benennt die echte Versuchung zur Übergeneralisierung.

### ❌ Schlecht: Platzhalter ohne Substanz

```markdown
### Allowed Claims
- Spec-First ist gut.

### Disallowed Claims
- ...
```

**Warum schlecht:** „Spec-First ist gut" ist keine falsifizierbare, kontextgebundene Aussage. `Disallowed Claims` ist leer — der Claim-Raum ist unbegrenzt offen, was epistemisch wertlos ist.

## Lokale Validierung

```sh
make validate-epistemics
```

Gibt `exit 1` mit konkreter Fehlermeldung pro Experiment, wenn ein `adopted`-Experiment den Block nicht oder unvollständig hat.

## Hinweis

Der Block ist ein **Zwang zur Artikulation** — kein Wahrheitsgarant. Seine Wirkung hängt am Review-Verhalten: Ein mechanisch ausgefüllter Block ohne Nachdenken ist formal korrekt und inhaltlich hohl. Die epistemische Qualität entsteht im Schreiben und im Review, nicht im Feld.
