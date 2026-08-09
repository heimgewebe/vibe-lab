# Vibe-Lab

**Verbrauchergebundener Experiment- und Evidenzraum für überprüfbare Arbeitsweisen.**

Vibe-Lab hält rohe Beobachtungen fest, registriert begrenzte Vergleiche vor ihrer Ausführung, bindet Ergebnisse an konkrete Evidenz und schließt sie mit einer überprüften Entscheidung ab.

Es ist kein Agentenlaufzeitsystem, Scheduler, Dashboard, zweites Bureau, zweiter Grabowski-Governor oder automatische Lerninstanz. GitHub, CI, Grabowski, RepoGround und Bureau bleiben die jeweiligen Wahrheits- und Entscheidungsorgane.

## Schnellstart

### 💡 Rohe Idee festhalten

Lege eine Markdown-Datei in `raw-vibes/` an:

```bash
echo "# Meine Beobachtung\n\nEin begrenzter Kontext scheint bei dieser Aufgabenklasse weniger Fehlpfade zu erzeugen ..." \
  > raw-vibes/context-observation.md
```

Kein Schema, kein Frontmatter, keine CI-Prüfung. Eine rohe Idee ist noch keine Wirkungsaussage und keine Aufgabe.

### 🧪 Strukturiertes Experiment starten

Nur wenn eine reale Entscheidung und ein Verbraucher benannt sind:

1. Erstelle ein Issue mit dem Formular **🧪 Experiment Proposal**.
2. Kopiere `experiments/_template/` in einen neuen Ordner.
3. Fülle `manifest.yml`, `method.md`, `CONTEXT.md` und `registration.v2.json` aus.
4. Friere bestätigten externen Consumer, Decision-Referenz, Kontrolle, Behandlung, numerische Ergebnisgrenzen, Surface-Budget, Registrierungszeitpunkt, Reviewdatum, Ablauf und reviewed Outcome-Zuordnung vor der Beobachtung ein.
5. Sammle Evidenz in `evidence.jsonl` oder über die evidenzgebundene Beobachtungsaufnahme.

### 📚 Ergebnis übernehmen

Erst wenn ein Experiment belastbare Evidenz und einen benannten externen Verbraucher besitzt:

1. Erstelle einen Pull Request mit dem Template **Promotion**.
2. Alle Pflichtartefakte müssen vollständig sein (`make validate`).
3. Review und Merge dokumentieren die Vibe-Lab-Entscheidung.
4. Die tatsächliche Übernahme in ein Produktrepo, Bureau oder Grabowski bleibt eine eigene Entscheidung des zuständigen Organs.

## Aktive Experimente

`experiments/active.v1.json` ist die einzige begrenzte Wahrheit über laufende Experimente. Historische Verzeichnisse sind nicht automatisch aktiv. Maximal fünf Experimente dürfen gleichzeitig aktiv sein. Der aktuelle Bestand wird im README bewusst nicht gespiegelt, damit kein zweiter, schnell veraltender Status entsteht.

```bash
python3 scripts/docmeta/validate_active_experiments.py
```

Der Validator bindet jeden aktiven Eintrag an `results/decision.yml`. Bei registrierten Experimenten müssen Verbraucher, Entscheidungsfrage, primäre Messgröße, Reviewdatum und Ablaufdatum exakt mit der Registrierung übereinstimmen. Neue Ordner benötigen unabhängig von ihrem Datumspräfix den aktuellen v2-Vertrag; nur die beim T005-Preimage bereits vorhandenen Experiment-IDs bleiben als geschlossener Altbestand kompatibel.

Neue Experimente verwenden `registration.v2.json`. `tools/vibe-cli/capture_effect_observation.py` erfasst registrierungs- und evidenzgebundene Beobachtungen atomar. `tools/vibe-cli/evaluate_effect.py` wertet begrenzte Vergleiche deterministisch aus. Beide Werkzeuge sind Review-Werkzeuge und besitzen keine automatische Policy-, Routing-, Queue-, Merge- oder Runtime-Autorität.

### Lokal validieren

```bash
python3 -m pip install -r requirements.txt
make validate
```

## Drei Phasen, aufsteigende Strenge

| Phase | Ort | Anforderung | Charakter |
|-------|-----|-------------|-----------|
| **Roh** | `raw-vibes/` | Keine | Beobachtung oder Idee ohne Wirkungsanspruch |
| **Experiment** | `experiments/` | Verbraucher, Registrierung, Methode, Evidenz, Ablauf | Prospektiv und überprüfbar |
| **Bibliothek** | `catalog/`, `prompts/adopted/` | Vollständige Validierung und realer Verbraucher | Bewusst übernommene Praxis |

**Prinzip:** Leicht am Eingang, hart am Ausgang.

## Projektstruktur

```text
vibe-lab/
  raw-vibes/                      # Rohe Ideen, Notizen, Fragmente
  experiments/                    # Registrierte Tests und historisches Archiv
  catalog/                        # Validierte, konsumierte Erkenntnisse
  prompts/                        # Menschenlesbare Bibliotheksartefakte
  benchmarks/                     # Vergleichsaufgaben
  instruction-blocks/             # Portable Denkbausteine
  decisions/                      # Meta- und Abschlussentscheidungen
  docs/                           # Grundlagen, Pläne, Berichte und Playbooks
  contracts/                      # Kanonische und policy-nahe Verträge
  schemas/                        # Validierungsschemas
  scripts/                        # Guard- und Generatorstack
  tests/                          # Fixture- und Contract-Tests
  tools/                          # Begrenzte CLI-Werkzeuge
  exports/                        # Generierte Kompatibilitätsflächen
  .vibe/                          # Repo-operative Verträge
```

## Zuständigkeitsgrenze

Vibe-Lab darf:

- eine prospektive Vergleichsfrage registrieren;
- Beobachtungen an Evidenz binden;
- Claims, Vergleichbarkeit, Unsicherheit und Nichtaussagen prüfen;
- wiederkehrende Reibung als Vorschlag für das Bureau dokumentieren;
- Experimente fördern, pilotieren, zurückstellen, verwerfen oder archivieren.

Vibe-Lab darf nicht:

- die nächste Aufgabe auswählen;
- Bureau-Queues verändern;
- Pull Requests mergen oder Dienste deployen;
- GitHub-, CI-, Runtime- oder RepoGround-Wahrheit überschreiben;
- aus einer einzelnen Beobachtung eine allgemeine Regel machen.

## Steuerung und Wahrheitshierarchie

| Dokument | Zweck | Status |
| --- | --- | --- |
| `repo.meta.yaml` | Maschinenlesbare Repo-Verfassung | Kanonisch |
| `AGENTS.md` | Bindende Leseregeln | Kanonisch |
| `agent-policy.yaml` | Operative Agentengrenzen | Kanonisch |
| `docs/foundations/vision.md` | Begrenztes Zielbild | Grundlagendokument |
| `docs/foundations/repo-plan.md` | Architektur- und Umsetzungsrahmen | Grundlagendokument |
| `experiments/active.v1.json` | Laufende Experimentwahrheit | Operativ, validiert |

**Wahrheitshierarchie:**

1. kanonische Steuerungsquellen — `repo.meta.yaml`, `AGENTS.md`, `agent-policy.yaml`, `contracts/*`, `schemas/*`;
2. Grundlagenquellen — `docs/foundations/vision.md`, `docs/foundations/repo-plan.md`;
3. operative Dokumente und aktive Experimentwahrheit;
4. Navigation;
5. generierte Diagnoseflächen.

## Weiterführend

- [Contributing](CONTRIBUTING.md)
- [Vision](docs/foundations/vision.md)
- [Optimierungsplan](docs/plans/vibe-lab-optimization-plan-v1.md)
- [Produktive Zuständigkeitsgrenze](docs/ecosystem/vibe-lab-productive-role.md)
- [Validatorinventar und Survivor-Status](docs/reports/vibe-lab-validator-inventory-v1.md)
- [Dokumentation](docs/index.md)
