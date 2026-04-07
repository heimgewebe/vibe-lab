# 🎮 Challenge 3: Legacy-Code Refactoring

## Beschreibung

Refactore den folgenden **absichtlich schlecht geschriebenen Code** in sauberen, wartbaren, getesteten Code.

## Der Legacy-Code

```javascript
// legacy-user-service.js - NICHT anfassen, als Ausgangspunkt verwenden
function doStuff(d, t, x) {
  var result = [];
  for (var i = 0; i < d.length; i++) {
    if (d[i].t == t) {
      if (x == true) {
        if (d[i].a == true && d[i].s != 'deleted') {
          var obj = {};
          obj.n = d[i].n;
          obj.e = d[i].e;
          obj.t = d[i].t;
          obj.created = d[i].c;
          if (d[i].p != undefined && d[i].p != null && d[i].p != '') {
            obj.phone = d[i].p;
          }
          result.push(obj);
        }
      } else {
        if (d[i].s != 'deleted') {
          var obj = {};
          obj.n = d[i].n;
          obj.e = d[i].e;
          obj.t = d[i].t;
          obj.created = d[i].c;
          if (d[i].p != undefined && d[i].p != null && d[i].p != '') {
            obj.phone = d[i].p;
          }
          result.push(obj);
        }
      }
    }
  }
  result.sort(function(a, b) {
    if (a.n < b.n) return -1;
    if (a.n > b.n) return 1;
    return 0;
  });
  return result;
}

function addThing(d, n, e, t, p) {
  for (var i = 0; i < d.length; i++) {
    if (d[i].e == e) {
      return { error: 'already exists' };
    }
  }
  d.push({ n: n, e: e, t: t, p: p, a: true, s: 'active', c: new Date().toISOString() });
  return { success: true };
}
```

## Anforderungen

### Muss
- TypeScript-Migration
- Aussagekräftige Funktions- und Variablennamen
- Typ-Definitionen für alle Datenstrukturen
- DRY – keine Code-Duplizierung
- Mindestens 10 Tests, die das Verhalten des Original-Codes abdecken
- Gleiche Funktionalität wie das Original

### Soll
- Error Handling mit spezifischen Error-Types
- Immutable Datenstrukturen (kein Mutieren des Input-Arrays)
- JSDoc-Kommentare
- Input-Validierung

## Bewertungskriterien

| Kriterium | Gewicht |
|-----------|---------|
| Gleiche Funktionalität? | 25% |
| Code-Lesbarkeit und Benennung | 25% |
| TypeScript-Typisierung | 20% |
| Tests (Abdeckung und Qualität) | 20% |
| Zusätzliche Verbesserungen | 10% |

## Zeitmessung

Stoppe die Zeit von der ersten Interaktion bis zum fertigen Refactoring.

## Ergebnis-Template

```yaml
challenge: legacy-refactoring
style: [verwendeter Stil]
techniques: [verwendete Techniken]
tool: [verwendetes Tool]
time_minutes: [Gesamtzeit]
iterations: [Anzahl Prompt-Iterationen]
result:
  functionality_preserved: true/false
  readability: 1-5
  typescript_quality: 1-5
  test_quality: 1-5
  additional_improvements: 1-5
notes: "..."
```
