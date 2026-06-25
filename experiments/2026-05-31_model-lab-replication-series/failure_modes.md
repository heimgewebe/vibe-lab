---
title: "Model-Lab Replication-Series — Failure Modes"
status: designed
canonicality: operative
---

# Model-Lab Replication-Series — Failure Modes

## Wann scheitert der Ansatz oder führt in die Irre?

### Versuchsdesign

- **Kosmetische Umbenennung:** Ein neues Label oder eine geringfügige Textänderung erzeugt noch keinen materiellen Kontrast.
- **Mehrere unkontrollierte Achsen:** Nicht deklarierte Unterschiede verhindern die Zuordnung eines späteren Befunds zur gewählten Intervention.
- **Drift bei Challenge, Akzeptanz, Bewertung oder Tests:** Unterschiedliche Ergebnisflächen erzeugen einen ungültigen Vergleich.
- **Ungleiche Laufzeitbedingungen:** Modell, Werkzeuge, Berechtigungen, Sampling, Abhängigkeiten, Laufzeitumgebung, Harness und menschliche Eingriffe müssen vor einer Ausführung gleich gebunden werden.
- **Nachträgliche Änderung:** Wird eine Bedingung nach Sichtung eines Ergebnisses verändert, ist der eingefrorene Vergleich ungültig.
- **Selbstauskunft als Unabhängigkeitsbeweis:** Ein getrennter Kontext belegt keine extern attestierte Modellunabhängigkeit.
- **Historische Runs als nachträglich konstruierte Kontrolle:** Run-001, Run-002 und Run-003 bleiben historischer Kontext.

### Grenzen des Design-Artefakts

- **Design mit Ausführungsfreigabe verwechselt:** Ein gültiges Design erlaubt keinen Run, keine Messung und keine Ergebnisbewertung.
- **Freeze mit Laufzeitbindung verwechselt:** Ein eingefrorenes Bundle kann weiterhin ungebundene Laufzeitwerte besitzen.
- **Grüner Validator mit empirischem Ergebnis verwechselt:** Strukturelle Gültigkeit ist kein Nachweis eines Effekts oder einer Qualitätsüberlegenheit.
- **Zugewiesene Instruktion mit beobachteter Befolgung verwechselt:** Compliance, Kontamination und Reihenfolge müssen erst in einer späteren Ausführung beobachtet werden.
- **Prozessartefakt als Ergebnis gewertet:** Eine Treatment-spezifische Vorab-Spezifikation ist Teil der Intervention und kein zusätzlicher Qualitätsgewinn.
- **Ein einzelnes Paar als Kausalbeweis behandelt:** Auch ein später ausgeführtes Paar isoliert nicht automatisch einzelne Promptbestandteile.

### Prompt-Scope

- **Das Bündel wird als Einzeleffekt interpretiert:** Die Treatment-Intervention umfasst Spezifikationspflicht, Implementierungsreihenfolge, Vollständigkeitsprüfung, Format- und Constraint-Beispiele, Promptlänge, interne Struktur, Direktionsstärke, motivationale Rahmung und Pflichtabschnitte.
- **Ein Einzelbestandteil wird zur Ursache erklärt:** Ein späterer Befund darf höchstens dem vollständigen Bündel zugeordnet werden, nicht einem Satz, der kanonischen Spec-First-Formulierung, der Länge, der Struktur oder den Beispielen allein.
- **Falsche Konstanten werden behauptet:** Konstant sind nur Sprache, Berechtigungen, Kompositionsreihenfolge, Benchmark und gemeinsame Bedingung.
- **Control wird zu einer Gegeninstruktion:** Control ist die neutrale Abwesenheit der zusätzlichen positiven Workflow-Anforderung, nicht ein Verbot von Spezifikation.
- **Experimentmetadaten werden ausgeliefert:** Rollen, Achse, Hypothese und Vergleichsrahmung dürfen nicht in Shared Condition oder Overlays gelangen.
- **Freitext driftet vom strukturierten Ursprung weg:** Operative Promptdateien müssen deterministisch aus der strukturierten Quelle erzeugt und bytegenau geprüft werden.

### Provenienz und Freeze

- **Interne Hashkonsistenz wird mit Herkunft verwechselt:** Der Validator muss bei jedem Lauf das historische Git-Objekt an `source_commit_sha:source_path` lesen und Bytegleichheit mit dem Snapshot verlangen.
- **Fehlende Historie wird als Erfolg behandelt:** Fehlender Commit, unvollständiger Checkout, fehlender historischer Pfad oder abweichende Bytes müssen fail-closed enden.
- **Richtige Bytes werden der falschen Rolle zugeordnet:** Kanonischer Quellpfad, `artifact_type` und gemeinsamer Source-Commit müssen zusätzlich gebunden sein.
- **Reduzierte Vorbedingung ersetzt die vollständige Gate-Wahrheit:** Erforderliche Dimensionen und Confounder werden aus dem eingefrorenen vollständigen Gate abgeleitet.
- **Korrekte SHA-256-Werte werden mit semantischer Gültigkeit verwechselt:** Hashes belegen weder Rollenidentität noch methodische Ehrlichkeit.
- **Ein offenes Dateiverzeichnis wird als geschlossenes Bundle behandelt:** Undeklarierte, entkommene, aliasierte oder symbolisch verlinkte Dateien müssen den Freeze ungültig machen.
- **Das Manifest behauptet seine eigene finale Commit-Identität:** Ein Freeze-Manifest darf sich nicht selbst hashen und keinen finalen Head oder Tree als eigene Herkunft festschreiben.

### Auslieferung und Messung

- **Komponenten zeigen auf dieselbe Datei:** Benchmark, Shared Condition und Overlays müssen die deklarierten, voneinander getrennten Dateien sein.
- **Textnormalisierung wird nicht geprüft:** Ausgelieferter Text muss UTF-8, LF-only und mit abschließendem Newline gespeichert sein.
- **Abbruchzeit wird als validierte Änderungszeit behandelt:** Vor bestandenem gemeinsamem Verifikationsschritt bleibt `time_to_validated_change_seconds` null.
- **Fehlende Evidenz wird als Problemlosigkeit gedeutet:** Fehlende Compliance-, Kontaminations-, Provenienz-, Verifikations- oder Messdaten blockieren eine spätere Interpretation.

Ein Contract kann belegen, dass eine Grenze deklariert und mechanisch bewahrt wurde. Er kann nicht allein belegen, dass der Versuch lief, ein kausaler Effekt besteht oder eine Qualitätsentscheidung gerechtfertigt ist.
