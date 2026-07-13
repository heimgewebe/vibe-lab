---
title: "Repository-Plan"
status: active
canonicality: foundational
updated: "2026-07-13"
---

# Repository-Plan für Vibe-Lab

## Zielbild

Vibe-Lab ist ein begrenzter, verbrauchergebundener Experiment- und Evidenzraum. Das Repository unterstützt eine konkrete unsichere Entscheidung durch:

1. billige Erfassung einer rohen Beobachtung;
2. prospektive Registrierung eines Vergleichs;
3. evidenzgebundene Beobachtungsaufnahme;
4. deterministische, nicht autorisierende Auswertung;
5. überprüfte Abschlussentscheidung;
6. Archivierung oder bewusste Übernahme durch ein zuständiges Organ.

Der Plan optimiert nicht auf Funktionsbreite, sondern auf geringe aktive Oberfläche, klare Wahrheitsgrenzen und ehrliche Abbruchentscheidungen.

## Nichtziele

Vibe-Lab wird nicht zu:

- Agentenlaufzeit oder Agenten-Orchestrator;
- Scheduler, Queue oder Aufgabenregister;
- Dashboard oder Leitstand;
- Runtime-, Deploy-, Merge-, Routing- oder Policy-Autorität;
- zweitem Bureau oder zweitem Grabowski-Governor;
- allgemeinem Heimlern-, Plexer- oder Chronik-Dienst;
- automatischer LLM-basierter Mustererkennung;
- neuer breiter, instruktionsführender Tool-Projektionsschicht.

Bestehende generierte Kompatibilitätsmarker und ihre blocking Paritätsverträge bleiben aktiv, solange die operativen Verträge sie verlangen. Historische Dateien, frühere Pläne und vorhandene Validatoren autorisieren keine neue Expansion.

## Wahrheit und Zuständigkeit

Die Wahrheitshierarchie wird durch `repo.meta.yaml` definiert. Für den operativen Zustand gelten zusätzlich folgende Grenzen:

- `experiments/active.v1.json` ist die einzige Wahrheit über aktive Experimente;
- GitHub und CI sind Wahrheit für Code-, Review-, Merge- und Prüfzustände;
- Grabowski ist Wahrheit für ausgeführte Operatorarbeit und Receipts;
- RepoBrief / Lenskit ist Quelle für zitierbaren Repository-Kontext;
- Bureau ist Wahrheit für Aufgaben, Prioritäten und Promotionen;
- Vibe-Lab bewahrt nur Experimentdesign, Evidenzbindung, Auswertung und Abschluss.

Generierte Dateien unter `docs/_generated/` sind Diagnoseflächen. Sie werden nicht manuell editiert und besitzen keine Entscheidungsautorität.

## Zonenmodell

### 1. Capture-Zone

Pfad: `raw-vibes/`

Zweck: Beobachtungen, Fragen und Ideen ohne Schema- oder Wirkungsanspruch billig festhalten.

Eine rohe Notiz:

- ist kein aktives Experiment;
- ist keine Bureau-Aufgabe;
- ist keine adoptierte Praxis;
- erzeugt keine automatische Folgearbeit.

### 2. Active-Experiment-Zone

Pfade: `experiments/active.v1.json` und die dort referenzierten Experimentordner.

Jedes neue Experiment benötigt:

- benannten Verbraucher;
- konkrete Entscheidungsfrage und Eigentümer;
- Kontrolle und Behandlung;
- primäre Messgröße und Mindestwirkung;
- Vergleichbarkeitsgrenzen und bekannte Störfaktoren;
- erlaubte Evidenzquellen;
- unabhängige Beobachtung;
- Reviewdatum und Ablauf;
- erlaubte Abschlussausgänge.

Maximal fünf Experimente dürfen aktiv sein. Ein Ordner wird nicht durch seine Existenz aktiv.

### 3. Review- und Entscheidungszone

Pfade: Experimentergebnisse, `decisions/` und begrenzte CLI-Werkzeuge unter `tools/vibe-cli/`.

Die Review-Schicht darf:

- Evidenzidentität und Schemaform prüfen;
- doppelte oder nach Ablauf erfasste Beobachtungen blockieren;
- Vergleichbarkeit, Unabhängigkeit, Verblindung, Aufwand und Unsicherheit ausweisen;
- `promote`, `pilot`, `defer`, `reject` oder `archive` vorschlagen und dokumentieren.

Sie darf keine externe Mutation auslösen. Eine Promotion in Bureau, Grabowski oder einem Produktrepo bleibt eine eigene Entscheidung dieses Organs.

### 4. Bibliothek und Archiv

Pfade: `catalog/`, `prompts/`, `benchmarks/`, `instruction-blocks/`, `experiments/_archive/` und historische Experimentordner.

Ein Bibliotheksartefakt gilt nur dann als aktiv, wenn ein externer Verbraucher, ein Entscheidungsziel und eine Reviewregel benannt sind. Sonst ist es historischer Bestand.

Archive bewahren Provenienz und Fehlversuche, ohne alte Speziallogik automatisch dauerhaft blocking zu halten.

## Minimaler aktiver Kern

Der dauerhaft gerechtfertigte Kern besteht aus:

- aktiver Experimentliste;
- prospektiven Registrierungs- und Ergebnisschemas;
- generischen Schema-, Relation-, Run-Bundle-, Claim/Evidence- und Promotion-Gates;
- evidenzgebundener Beobachtungsaufnahme;
- deterministischer Review-Auswertung;
- expliziten Abschlussentscheidungen;
- generiertem Index und Drift-Schutz für kanonisch abgeleitete Dateien;
- bestehenden Kompatibilitätsmarkern, solange operative Verträge und CI sie verlangen.

Neue dauerhafte Komponenten benötigen einen aktuellen Verbraucher und eine benannte Fehlerklasse. Sie müssen mehr Risiko oder Wartung entfernen, als sie hinzufügen.

## Validierungsarchitektur

Die Prüfoberfläche ist in drei Gruppen getrennt:

1. **Core** — generische Verträge und Evidenzintegrität für das gesamte Repository;
2. **Active** — Spezialprüfungen für tatsächlich aktive Experimente und eingefrorene Abschlüsse;
3. **Legacy** — historische Spezialprüfungen mit befristeter Weiterführung.

Alle `validate-*`-Ziele müssen im maschinenlesbaren Inventar klassifiziert sein. Neue Spezialvalidatoren sind nur erlaubt, wenn eine generische Prüfung den benannten Fehler nicht ausreichend abdeckt.

Ein Legacy-Validator wird nur entfernt, wenn mindestens ein materieller Beleg vorliegt:

- seine Artefaktfamilie ist geschlossen und archiviert und kein aktiver Import besteht; oder
- ein Core-Validator deckt dieselbe Fehlerklasse und relevante Fixtures nachweislich ab.

Der head- und diffgebundene Review des Entfernungs-PR prüft diesen Beleg und die Integrationsfolgen; er ersetzt den materiellen Beleg nicht.

Der Reviewtermin für den aktuellen Legacy-Bestand ist 2026-09-01. Zielrichtung ist eine Reduktion um 30–50 Prozent, nicht blindes Löschen.

## Aktueller Umsetzungsstand

Stand 13. Juli 2026:

- Operator-Lab mit 36 Karten eingefroren: `insufficient_evidence`;
- aktive Experimentwahrheit eingeführt;
- prospektive Registrierung v2 eingeführt;
- evidenzgebundene atomare Beobachtungsaufnahme vorhanden;
- deterministischer Effekt-Evaluator als unpromotetes Review-Werkzeug vorhanden;
- praktisch nicht ausführbarer Operator-Interventions-Pilot archiviert;
- aktive Custom-Agenten und instruktionsführende Cursor-/Copilot-Projektionsinhalte stillgelegt; generierte Kompatibilitätsmarker und Paritätsverträge bleiben aktiv;
- Validatorfläche gruppiert: 45 Core, 10 Active, 48 Legacy und 2 Supplemental;
- ein aktiver RepoBrief-Workbench-Pilot mit Review am 15. August 2026 und Ablauf am 1. September 2026.

## Nächste Phasen

### Phase E1 — Wahrheitsausrichtung

- kanonischen Zweck gegen die begrenzte Rolle prüfen; Änderungen an `repo.meta.yaml` bleiben menschlich gepflegt;
- Vision, Repository-Plan, README, Roadmap und operative Berichte angleichen;
- veraltete aktive Zahlen und frühere Expansionsziele entfernen;
- keine neue Funktion hinzufügen.

Erfolg: Alle agentenseitig änderbaren maßgeblichen Dokumente beschreiben dieselbe begrenzte Rolle; kanonische Quellen bleiben unverändert oder werden separat menschlich gepflegt.

### Phase E2 — Legacy-Survivor-Audit

Prüfreihenfolge:

1. Agent-Handoff-, Agent-Command- und Command-Chain-Verträge;
2. geschlossene Model-Lab-Spezialprüfungen;
3. historische Replay-, Fixture- und Cross-Contract-Semantik;
4. rLens- und PR-Context-Prüfungen nach Abschluss des aktiven RepoBrief-Piloten.

Erfolg: Jeder Legacy-Validator besitzt `retain_with_consumer`, `covered_by_core` oder `retire`; jede Entfernung beruht auf Archiv- oder Gleichwertigkeitsbeleg.

### Phase E3 — Aktiven Pilot schließen

Den RepoBrief-Workbench-Piloten spätestens am Ablaufdatum mit einer überprüften Entscheidung schließen. Ohne prospektive Vergleichsevidenz keine Default-Promotion.

Erfolg: klare Entscheidung, aktualisierte Active Registry und keine automatische Verlängerung.

### Phase E4 — Bibliotheksverbrauch prüfen

Katalog, Prompts, Benchmarks und Instruction Blocks auf reale Verbraucher prüfen. Nicht konsumierte Flächen archivieren oder als historisch kennzeichnen; keine neue instruktionsführende Exportprojektion allein zur Pfaderhaltung bauen. Bestehende Kompatibilitätsmarker bleiben erhalten, bis ihre operativen Verträge separat geändert werden.

Erfolg: Jede aktive Bibliotheksfläche hat Verbraucher, Entscheidungsziel und Reviewregel.

## Stopregeln

Ein Vorhaben wird beendet oder archiviert, wenn es:

- einen neuen Dienst, eine Datenbank oder ein Dashboard benötigt;
- automatische Bureau-, Runtime-, Routing-, Merge- oder Deploy-Mutationen einführt;
- synthetische produktive Wiederholungen oder retrospektive Kennzahlerfindung verlangt;
- mehr dauerhafte Spezialvalidatoren hinzufügt, als es entfernt;
- nach Ablauf keine reale Entscheidung beeinflusst;
- nur interne Konsistenz oder Dokumentmenge als Nutzen ausweist.

## Akzeptanzkriterien für das reduzierte Vibe-Lab

Vibe-Lab gilt als tragfähig, wenn:

- höchstens fünf aktive Experimente existieren;
- jedes aktive Experiment Verbraucher, Entscheidungsziel, Review und Ablauf besitzt;
- keine Runtime-, Queue-, Routing-, Merge-, Deploy- oder Policy-Autorität besteht;
- Promotionen an konkrete Evidenz und externe Verbraucher gebunden sind;
- unzulässige Wirkungsbehauptungen und methodisch nicht ausführbare Versuche geschlossen werden;
- die Legacy-Prüfoberfläche planmäßig sinkt;
- der Wartungsaufwand in einem vertretbaren Verhältnis zu verhinderten Fehlern oder verbesserten Entscheidungen steht.
