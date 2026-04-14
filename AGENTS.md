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
- **`anecdotal` begrenzt Schlussfolgerungen.** Evidenz auf Niveau `anecdotal` (Einzelbeobachtung, eine Session, eine Person) trägt keine allgemeinen Aussagen. Schlüsse aus anecdotal-Evidenz müssen explizit als kontextspezifisch und nicht generalisierbar markiert sein.
- **Enge Datenbasis ≠ breite Gültigkeit.** Beobachtungen aus einem engen Kontext (Sprache, Modell, Person, Zeitpunkt) dürfen nicht als allgemeingültig formuliert werden. Geltungsansprüche müssen den tatsächlichen Beobachtungsumfang widerspiegeln.
- **Artefakt ≠ Erkenntnis.** Das Erzeugen von Artefakten (result.md schreiben, evidence.jsonl befüllen, Ordner anlegen) ist keine epistemische Handlung. Erkenntnisgewinn entsteht nur durch belegte Beobachtung und explizite Auswertung — nicht durch die Produktion von Dateien.
- **Behauptungen brauchen Rückverweis.** Jede Schlussfolgerung in `result.md`, `decision.yml` (rationale) oder PR-Beschreibungen muss auf konkrete Einträge in `evidence.jsonl` oder andere benannte Belege rückführbar sein. Unbelegte Aussagen im Freitext sind unzulässig.
- **Zieltypen explizit halten.** Analyse (Verstehen, Messen, Interpretieren) und Konstruktion (Bauen, Anlegen, Ändern) sind verschiedene Zieltypen. Agenten dürfen innerhalb einer Aufgabe nicht undeklariert zwischen ihnen wechseln; jeder Wechsel muss explizit benannt werden.
- **Manifest-Felder spiegeln Ist-Zustand.** `status`, `execution_status` und `updated` im manifest.yml müssen den tatsächlichen Zustand des Experiments widerspiegeln — nicht den beabsichtigten. Bei Abweichung zwischen Manifest-Feldern und vorliegenden Artefakten ist das Manifest sofort zu korrigieren.
