# AGENTS.md — Bindende Leseregeln für Agenten

> Dieses Dokument ist handgepflegt und kanonisch. Es wird nicht generiert.

## Lesereihenfolge

Agenten MÜSSEN Dokumente in dieser Reihenfolge lesen:

1. `repo.meta.yaml` — Maschinenlesbare Repo-Verfassung
2. `AGENTS.md` — Dieses Dokument
3. `agent-policy.yaml` — Operative Agentensteuerung
4. `README.md` — Projekteinstieg
5. `docs/index.md` — Navigation
6. Kanonische Pfade (`contracts/`, `schemas/`, `.vibe/`)
7. `docs/_generated/*` — Diagnose (nur lesen, nie editieren)

## Wahrheitshierarchie

| Ebene        | Quellen                                               | Charakter              |
| ------------ | ----------------------------------------------------- | ---------------------- |
| Wahrheit     | `repo.meta.yaml`, `AGENTS.md`, `agent-policy.yaml`   | Kanonisch, handgepflegt |
| Wahrheit     | `vision.md`, `repo-plan.md`, `contracts/*`, `schemas/*` | Kanonisch             |
| Operativ     | `README.md`, `CONTRIBUTING.md`, `.vibe/*`             | Handgepflegt           |
| Navigation   | `docs/index.md`                                       | Wegweiser              |
| Diagnose     | `docs/_generated/*`                                   | Maschinell, read-only  |

**Regel:** Bei Widersprüchen gilt die höhere Ebene.


### Definitionen (canonicality & status)

- **canonical**: verbindliche, langfristige Referenz
- **operative**: aktiv genutzte Arbeitsgrundlage
- **navigation**: orientierende Einstiegs- und Wegweiserdokumente; helfen beim Auffinden relevanter kanonischer oder operativer Inhalte
- **diagnosis**: diagnostische Sicht auf Zustände, Prüfungen oder abgeleitete Befunde; informativ, aber nicht maßgeblich gegenüber kanonischen Quellen
- **derived**: aus anderen Quellen abgeleitet, nicht primär
- **exploratory**: dokumentierter Denk- und Optionsraum; bewusst nicht operativ bindend

*Hinweis zu `status: designed`:* `designed` ist primär experimentnah und bezeichnet geplante oder vorbereitete Zustände. Der Wert ist nicht als generischer Status für beliebige Dokumente zu verstehen.

## Generierte Artefakte

Die folgenden Pfade enthalten ausschließlich generierte Artefakte. Agenten dürfen sie lesen, aber **niemals manuell editieren**:

- `exports/`
- `.cursor/rules/`
- `docs/_generated/`

## Handgepflegte Steuerungsdokumente

Die folgenden Dokumente sind kanonisch und werden ausschließlich von Menschen gepflegt:

- `repo.meta.yaml`
- `AGENTS.md`
- `agent-policy.yaml`

## Verhaltensregeln

1. **Abbruch bei Konflikten:** Wenn ein generiertes Artefakt einer kanonischen Quelle widerspricht, bricht der Agent ab und meldet den Konflikt.
2. **Keine Eigeninterpretation:** Agenten ergänzen keine Konzepte, die nicht in den kanonischen Quellen angelegt sind.
3. **Transparenz:** Jede agentengesteuerte Änderung muss ihren Auslöser (`triggered_by`) dokumentieren.
4. **Zonenrespekt:** Die Dreiphasenlogik (Capture vs. Labor vs. Bibliothek) wird eingehalten. Capture-Artefakte (raw-vibes/) sind roh und unstrukturiert. Labor-Artefakte werden nicht ohne Promotion-Gate in die Bibliothek verschoben.
5. **Verbot unbelegter Status-Umdeutung:** Agenten dürfen den Status bestehender Experimente nicht ohne belegte Grundlage ändern. Erforderlich ist entweder (1) eine explizite Aussage im Experiment, (2) ein passendes Decision-Artefakt, oder (3) ein eindeutiger struktureller Hinweis. Fehlen belastbare Belege, bleibt der bestehende Status unberührt; epistemische Unklarheit ist explizit auszuhalten.

## Epistemische Kalibrierung

- **Rohzonen bleiben roh.** Keine Begründungspflicht, keine Reviewerwartung in `raw-vibes/`.
- **`designed ≠ executed`.** Entwurf, Durchführung, Beobachtung und Deutung müssen unterscheidbar bleiben. `execution_status: executed` oder `replicated` setzt nachvollziehbare Spur in `execution_refs` voraus (evidence.jsonl, Artefakt, Log, Ergebnisdatei).
- **Aufwertung braucht sichtbare Begründung.** Jeder Anstieg epistemischen Status (adopted, pattern, best practice) muss nachvollziehbar begründet sein.
- **Claim-Disziplin.** Aussagen müssen Evidenz und Kontext widerspiegeln: Schmale oder `anecdotal` Evidenz (eine Session, ein Modell, ein Zeitpunkt) trägt keine allgemeinen Schlüsse — Schlussfolgerungen sind explizit als kontextspezifisch zu formulieren. Das Erzeugen von Artefakten ist keine epistemische Handlung; Erkenntnisgewinn entsteht nur durch belegte Beobachtung und explizite Auswertung. Schlussfolgerungen in `result.md`, `decision.yml` oder PR-Beschreibungen müssen auf konkrete Einträge in `evidence.jsonl` oder benannte Belege rückführbar sein; Interpretation und Hypothesen sind zulässig, müssen aber als solche erkennbar bleiben.
- **Zieltypen explizit halten.** Analyse (Verstehen, Messen, Interpretieren) und Konstruktion (Bauen, Anlegen, Ändern) sind verschiedene Zieltypen. Agenten dürfen innerhalb einer Aufgabe nicht undeklariert zwischen ihnen wechseln; jeder Wechsel muss explizit benannt werden.
- **Manifest-Felder spiegeln Ist-Zustand.** `status`, `execution_status` und `updated` im manifest.yml müssen den tatsächlichen Zustand des Experiments widerspiegeln — nicht den beabsichtigten. Bei Abweichung zwischen Manifest-Feldern und vorliegenden Artefakten muss die Abweichung sichtbar gemacht werden. Korrekturen dürfen nicht die zeitliche Entwicklung oder den ursprünglichen Zustand verdecken.
- **Regeln bewusst erweitern oder ersetzen.** Neue Regeln sollen bestehende präzisieren, bündeln oder ersetzen. Addition ist nur zulässig, wenn ein klar neuer Fall vorliegt, der durch bestehende Regeln nicht sinnvoll erfasst wird.

  Vor jeder Ergänzung ist zu prüfen:
  1) Wird hier nur etwas Bestehendes neu formuliert? → dann ersetzen oder bündeln
  2) Ist das Problem strukturell lösbar (Schema, Constraints, Tooling)? → dann nicht hier

  Additive Regeln müssen begründen:
  - warum bestehende Regeln nicht ausreichen
  - warum keine Bündelung oder Ersetzung sinnvoll ist

  Gleichzeitig gilt:
  Bestehende Regeln sind bei Überlappung oder Redundanz aktiv zu bündeln oder zu entfernen.
