# Vibe-Lab: Die Meta-Engine

Das Vibe-Lab ist keine Dokumentation und kein Ideenarchiv. Es ist eine Maschine, die Workflows, Architekturen und Prompts permanent testet, zerstört und neu erzeugt.

Die Vision basiert nicht auf Konsens oder "Best-ofs", sondern auf einem radikalen Selektionsprozess. Nur Ideen, die Geschwindigkeit und Präzision unter Druck erhöhen, überleben.

Das System ist in drei zwingenden Layern aufgebaut:

## Layer 1: Core Engine (Der Mechanismus)

Die Core Engine definiert die physikalischen Gesetze des Vibe-Codings in diesem System.

- **Vibe Contracts (.vibe/ als Vertragszone)**
  Prompting ist obsolet. Stattdessen werden *Vibe Contracts* (Intent, Constraints, Quality Gates) genutzt, die deterministische Grenzen für Agenten setzen.
- **Pipeline-Exekution**
  Jede Interaktion ist eine Pipeline (Prepare Context → Generate → Validate → Decide), kein einzelner Request.
- **Zweischichtige Architektur**
  Eine strikte strukturelle Trennung:
  - **Labor-Schicht:** Schnelle, kurzlebige Experimente (Spikes, Combos).
  - **Bibliotheks-Schicht:** Bewiesene, überlebensfähige Patterns und Artefakte.
- **Artefakt-Zentrierung**
  Erkenntnisse müssen exekutierbar sein (z.B. `.cursor/rules`, `AGENTS.md`). Dokumentation ohne Anwendbarkeit wird gelöscht.

## Layer 2: Practice System (Die Zusammenarbeit)

Wie Mensch und Maschine auf Basis der Core Engine interagieren.

- **Katalogisierte Hypothesen**
  Stile, Tools und Workflows existieren nicht als "Wissen", sondern als testbare Einträge mit Status (idea → testing → adopted/rejected).
- **Strikte Selektions-Gates**
  Ideen bewegen sich nur durch harten Beweis (Evidence Level). Die Übergänge zwischen Labor und Bibliothek erfordern validierte Benchmarks, keine Meinungen.
- **Messbarkeit als Pflicht**
  Alle Experimente produzieren auswertbare Rohdaten (`decision.yml`, `evidence.jsonl`). Jedes Experiment zwingt zu einer binären Entscheidung (adopt | reject | iterate).
- **Konflikt-Toleranz durch Isolation**
  Widersprüchliche Philosophien werden nicht geglättet, sondern in isolierten Experimenten gegeneinander ausgespielt.

## Layer 3: Evolution System (Die Selbsterneuerung)

Wie das System wächst und Stagnation (den "Ideenfriedhof") verhindert.

- **Permanenter Durchfluss**
  Ideen müssen zirkulieren. Eine Idee, die zu lange ungetestet in der Inbox liegt, verfällt.
- **Systematischer Druck**
  Metriken wie *Time-to-Running* und *Acceptance Rate* erzeugen Selektionsdruck. Werkzeuge oder Muster, die Friktion erhöhen oder den Flow stören, werden aktiv ausgemustert.
- **Integration in Heimgewebe**
  Erfolgreiche Praktiken werden über `WGX` und Metarepo-Templates in das übergeordnete Ökosystem synchronisiert. Das Repo ist der Sensor, das Heimgewebe die ausführende Flotte.

---
*Stillstand ist ein Systemfehler. Das Repository ist ein Selektionsfilter für Exzellenz.*
