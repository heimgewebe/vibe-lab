# Repository-Plan für vibe-lab

## Zielbild: Exekutierbarer Erkenntnisraum
Das Repository ist ein exekutierbarer Erkenntnisraum. Es erfasst Vibe‑Coding‑Hypothesen, macht sie experimentierbar, zwingt zu Entscheidungen, konserviert Lerngewinne und liefert daraus praktische, wiederverwendbare Artefakte (Rules, Instructions, Prompt‑Bausteine, Workflows).

Die Vision „Sammlung → Erprobung → Validierung → Kreation“ wird als Pipeline mit asymmetrischer Rückkopplung umgesetzt. Nichts bleibt „nur Idee“, aber nichts wird unvalidiert zur „Best Practice“ erklärt.

### Epistemische Zustände und Repo-Mechanik
Das System trennt strikt zwischen Wissensreife (epistemischen Zuständen) und dem operativen Status.

**Mapping:**
*   **Roh** ↔ `Intake (Issue)`: Sammlung unsortierter Impulse.
*   **Getestet** ↔ `Experiment`: Strukturierte Prüfung in isolierter Umgebung.
*   **Bewährt** ↔ `Catalog Entry (Adopted)`: Validiere Practice, aufgenommen in die Bibliothek.
*   **Systemisch erweitert** ↔ `Export / Ecosystem Promotion`: Ausleitung als Tool-Instruktion oder Anstoß für neue Experimente.

Operativ durchlaufen Artefakte die Status: `idea` → `testing` → `adopted` / `rejected` → `deprecated`.

## Phasenmodell der Architektur
Um nicht an vorzeitiger Komplexität zu scheitern, gliedert sich der Aufbau in drei Phasen:

### A. Minimaler Kern (MVP)
*Zwingend erforderlich, um den Erkenntniskreislauf zu starten.*
*   **Intake:** GitHub Issues als primäre Einlassschleuse.
*   **Experiment-Engine:** `experiments/` Ordner mit Manifest, Methode, Entscheidung und Resultat.
*   **Minimaler Katalog:** `catalog/` für erste `adopted` Practices.
*   **Schema-Validierung:** Harte CI-Prüfung der Kernartefakte (`schemas/`).
*   **Promotion-Gate:** Zwingender PR-Prozess für Änderungen am Katalog.

### B. Frühe Verstärker
*Sinnvoll nach Stabilisierung des MVPs, erhöht die Systemqualität maßgeblich.*
*   **Instruction Blocks (IR) & Exports:** Einführung von `instruction-blocks/` und automatisierte Generierung der `exports/`.
*   **Benchmarks:** Erste Heuristiken zur Erfolgsmessung.
*   **Erweiterte Governance:** Feinere CODEOWNERS-Regeln und verfeinerte Status Checks.

### C. Spätphase / Optionale Schicht
*Erstrebenswert für Distribution und Skalierung im Ökosystem.*
*   **Docs-Site:** Generierte MkDocs-Site für Durchsuchbarkeit.
*   **Breitere Tool-Abdeckung:** Exports für weitere Agentensysteme.
*   **Erweiterte Metriken:** Automatisierte Erfassung quantitativer Daten.

## Kanonische Artefakte
Die Pipeline stützt sich auf sieben harte, schemavalidierte Artefaktarten:

1.  **Hypothese (Innovation)**: Problem, Hypothese, Erfolgskriterium, Scope. Formuliert als Issue-Formular.
2.  **Experiment**: Isolierter Ordner (Manifest, Methode, Resultat, Entscheidung, Evidenz). Der überprüfbare Prozess.
3.  **Decision Artifact (Meta-Entscheidung)**: Steuert das System selbst. Dokumentiert Metriken, Gate-Regeln, Re-/De-Katalogisierungen und Export-Ziele. Keine bloßen Notizen, sondern Workflow-treibende Elemente.
4.  **Catalog Entry (Practice / Anti-Pattern)**: Kuratierter Eintrag mit Status und Evidenz, verlinkt zwingend auf Experimente.
5.  **Combo**: Unterart des Katalogs (`catalog/combos/`). Getestete Synergien/Anti-Synergien (z.B. Stil + Tool).
6.  **Benchmarks**: Definition von Metriken (Time-to-Running, Rework-Zyklen). *Wichtig:* Dies sind Startheuristiken. Qualitative Begleitevaluierung bleibt essenziell, das System darf nicht ausschließlich auf das Messbare optimieren.
7.  **Instruction Block IR + Exports**: Engine-neutrale Repräsentation (IR), aus der spezifische Ziel-Artefakte generiert werden.

### Die drei Regulationsebenen
Zur Vermeidung von Drift sind drei Ebenen funktional strikt getrennt:
*   **`.vibe/`**: Operative Default-Verträge dieses spezifischen Repositories (Constraints, Quality Gates).
*   **`instruction-blocks/`**: Die kanonische, wiederverwendbare Zwischenrepräsentation (IR) von Instruktionen.
*   **`exports/`**: Die daraus generierten, tool-spezifischen Ziel-Artefakte (z.B. `.cursor/rules/`, `.github/copilot-instructions.md`).

## Workflow: Intake bis Export

### 1. Intake: Issue-First
Die primäre Intake-Logik ist **Issue-first**.
Ein YAML-basiertes Issue Form (`.github/ISSUE_TEMPLATE/idea.yml`) erfasst die Hypothese niedrigschwellig. Erst beim Übergang in den Status `testing` erfolgt die Materialisierung als Datei/Ordner im Repository (`experiments/`).

### 2. Experiment-Durchführung
Jedes Experiment materialisiert sich als Ordner (z.B. `experiments/2026-04-08_spec-first-vs-yolo/`) basierend auf einem Golden Skeleton:
*   `manifest.yml` (Setup, Hypothese, Metriken)
*   `results/decision.yml` (Adopt, Reject, Iterate; inkl. Rationale)
*   Begleitende Methoden- und Resultatsdokumente.

### 3. Katalogisierung (Promotion-PR)
Die Aufnahme in den `catalog/` erfolgt ausschließlich über einen "Promotion-PR".
Dieser Gate prüft hart:
*   Existiert ein vollständiges Experiment?
*   Sind Schemas valide?
*   Sind Export-Artefakte synchron?
*   Passieren die Quality Gates?

### 4. Generierung der Exports
Bei Änderungen an der IR (`instruction-blocks/`) zwingt die CI zur Synchronisation der `exports/`. Es werden keine Prompts manuell gepflegt, sondern ausschließlich Ziel-Artefakte abgeleitet.

## Governance und Sicherheit
Sicherheit und Qualitätsschranken sind als Produktfeature integriert:
*   **Zonen:** Klare Trennung zwischen Labor (frei, CI warnt nur) und Bibliothek (restriktiv, CI blockt).
*   **Ownership:** Pfadbasierte Zuweisungen über `CODEOWNERS` regeln Review-Zuständigkeiten (z.B. strengeres Review für `catalog/`).
*   **Sicherheit:** Dependabot für Supply-Chain, Secret Scanning für Leak-Prävention, OpenSSF Scorecard als Baseline.

## Vorgeschlagene Zielstruktur
*Die Struktur zeigt das Zielbild, wird aber inkrementell (MVP → Ausbau) besiedelt.*

```text
vibe-lab/
  README.md
  vision.md

  .github/
    ISSUE_TEMPLATE/
      idea.yml            # Primärer Intake
    PULL_REQUEST_TEMPLATE/
      experiment-run.md
      promotion.md        # Das harte Gate
    workflows/
      validate.yml        # CI Schema-Prüfung
    CODEOWNERS            # Pfadbasierte Governance

  .vibe/                  # Repo-operative Verträge
    intent.md
    constraints.yml
    quality-gates.yml

  .cursor/rules/          # Symlinks/generiert für lokale Nutzung
  AGENTS.md               # Generiert

  experiments/            # Materialisierte Testläufe
    _template/
    2026-04-08_spec-first/
      manifest.yml
      results/decision.yml

  catalog/                # Validiertes Wissen (Bibliothek)
    styles/
    workflows/
    combos/               # Kuratierte Synergien

  benchmarks/             # Startheuristiken & Messpunkte
    criteria.md

  instruction-blocks/     # Kanonische IR
    spec-first-vibe.yml

  exports/                # Tool-spezifische Ziele (Generiert)
    copilot/
    cursor/

  schemas/                # Datenmodelle für CI-Checks
    experiment.manifest.schema.json
    catalog.entry.schema.json

  tools/                  # CLI / Automatisierung
    validate/
```
