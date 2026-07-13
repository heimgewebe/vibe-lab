---
title: "Systemvision"
status: active
canonicality: foundational
updated: "2026-07-13"
---
# Vibe-Lab: begrenzter Experiment- und Evidenzraum

Vibe-Lab ist ein kleiner, verbrauchergebundener Erkenntnisraum für Arbeitsweisen im KI-gestützten Entwickeln. Sein Zweck ist nicht, Arbeit selbst zu steuern, sondern eine konkrete unsichere Entscheidung durch ein vorab festgelegtes Experiment, gebundene Evidenz und einen überprüften Abschluss zu unterstützen.

Vibe-Lab ist insbesondere **kein** Agentenlaufzeitsystem, Scheduler, Dashboard, zweites Bureau, zweiter Grabowski-Governor, Routingdienst oder automatische Lerninstanz.

## Zustände

Eine Idee kann vier Zustände durchlaufen:

1. **roh** — eine noch unverbindliche Beobachtung in `raw-vibes/`;
2. **registriert** — ein prospektives Experiment mit Verbraucher, Entscheidungsziel, Vergleich, Messung, Reviewdatum und Ablauf;
3. **abgeschlossen** — ein geprüftes Ergebnis mit expliziten Nichtaussagen und der Entscheidung `promote`, `pilot`, `defer`, `reject` oder `archive`;
4. **übernommen** — eine außerhalb von Vibe-Lab bewusst konsumierte Praxis oder ein Artefakt mit benanntem Eigentümer.

Historische Dateien werden nicht allein durch ihre Existenz aktiv. Die einzige Wahrheit über laufende Arbeit ist `experiments/active.v1.json`.

## Arbeitsprinzipien

### Verbraucher vor Experiment

Ein neues Experiment benötigt vor Beginn einen benannten Verbraucher und eine konkrete Entscheidung, die das Ergebnis verändern kann. Beobachtungen ohne Entscheidungsziel bleiben Rohmaterial oder Archiv.

### Vorab festlegen statt nachträglich passend machen

Kontrolle, Behandlung, primäre Messgröße, Mindestwirkung, Vergleichbarkeit, Falsifikationsgrenzen, Reviewdatum und Ablauf werden vor der Beobachtung eingefroren. Retrospektiv erfundene Kennzahlen oder künstliche Wiederholungen sind kein Ersatz.

### Evidenz binden

Beobachtungen verweisen auf konkrete Pull Requests, Commits, CI-Prüfungen, Receipts oder Dateien. Identität, Herkunft, Aktualität und Unsicherheit müssen sichtbar bleiben. Vibe-Lab ersetzt keine Live-Wahrheitsquelle.

### Beobachtung, Bewertung und Entscheidung trennen

Eine Beobachtung ist noch keine Wirkung. Ein wiederkehrendes Muster ist noch keine Kausalität. Eine intern korrekte Auswertung ist noch kein praktischer Nutzen. Entscheidungen müssen diese Grenzen ausdrücklich bewahren.

### Leicht am Eingang, hart am Ausgang

Rohe Ideen dürfen billig sein. Promotionen müssen teuer sein: vollständige Evidenz, benannter Verbraucher, nachvollziehbarer Review und klarer Eigentümer außerhalb von Vibe-Lab.

## Zuständigkeitsgrenze im Ökosystem

- **Grabowski** führt Arbeit aus und erzeugt operative Receipts.
- **GitHub und CI** sind Wahrheit für Code-, Review-, Merge- und Prüfzustände.
- **RepoBrief / Lenskit** liefern zitierbaren Repository-Kontext.
- **Bureau** entscheidet über Aufgaben, Prioritäten und Promotionen.
- **Vibe-Lab** entwirft begrenzte Vergleiche, bindet Beobachtungen, prüft Claims und bewahrt Abschlüsse.

Vibe-Lab darf keine Queue verändern, keine Aufgabe auswählen, keinen Pull Request mergen, keinen Dienst deployen und keine Runtime-, Routing- oder Policy-Entscheidung automatisch autorisieren.

## Erfolgskriterium

Vibe-Lab ist nur dann nützlich, wenn ein Experiment nachweisbar mindestens eines leistet:

- eine reale Entscheidung wird mit weniger Lokalisierungs-, Evidenz- oder Bewertungsfehlern getroffen;
- eine unzulässige Promotion oder Wirkungsbehauptung wird verhindert;
- ein wiederkehrendes Problem wird so belegt, dass ein zuständiges Organ eine klarere Folgemaßnahme entscheiden kann.

Dokumentmenge, Validatorzahl und interne Konsistenz sind keine eigenständigen Nutzenbelege.

## Kosten- und Stopregel

Jede aktive Fläche benötigt einen Verbraucher, eine benannte Fehlerklasse und eine Review- oder Ablaufregel. Historische Spezialvalidatoren werden entfernt, sobald ihre Artefaktfamilie archiviert ist oder generische Prüfungen dieselbe Grenze nachweislich schützen.

Ein Vorhaben wird gestoppt oder archiviert, wenn es einen neuen Dienst, eine Datenbank, ein Dashboard, eine LLM-basierte Mustererkennung, automatische Bureau-Mutationen oder mehr dauerhafte Spezialprüfungen als entfernte Altlasten erfordert.

## Selbstverbesserung

Vibe-Lab darf seine Mess- und Prüfverfahren überprüfen. Es darf daraus aber keine allgemeine Selbststeuerungsbehauptung ableiten. Selbstverbesserung ist nur dann belegt, wenn ein prospektiver Vergleich eine reale Entscheidung oder einen realen Fehler messbar verbessert und die zusätzliche Wartung rechtfertigt.
