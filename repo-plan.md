# Repository-Plan für vibe-lab

## Zielbild: Exekutierbarer Erkenntnisraum
Das Repository ist ein exekutierbarer Erkenntnisraum. Es erfasst Vibe‑Coding‑Hypothesen, macht sie experimentierbar, zwingt zu Entscheidungen, konserviert Lerngewinne und liefert daraus praktische, wiederverwendbare Artefakte (Rules, Instructions, Prompt‑Bausteine, Workflows).

Die Vision „Sammlung → Erprobung → Validierung → Kreation“ wird als Pipeline mit asymmetrischer Rückkopplung umgesetzt. Nichts bleibt „nur Idee“, aber nichts wird unvalidiert zur „Best Practice“ erklärt.

### Epistemische Zustände und Repo-Mechanik
Das System trennt strikt zwischen Wissensreife (epistemischen Zuständen) und dem operativen Status.

**Mapping:**
*   **Roh** ↔ `Intake (Issue)`: Sammlung unsortierter Impulse.
*   **Getestet** ↔ `Experiment`: Strukturierte Prüfung in isolierter Umgebung.
*   **Bewährt** ↔ `Catalog Entry (Adopted)`: Validierte Praxis, aufgenommen in die Bibliothek.
*   **Systemisch erweitert** ↔ `Export / Ecosystem Promotion`: Ausleitung als Tool-Instruktion oder Anstoß für neue Experimente.

Operativ durchlaufen Artefakte die Status: `idea` → `testing` → `adopted` / `rejected` → `deprecated`.

**Unterscheidung Rejected vs. Deprecated:**
*   **`rejected`**: Eine Hypothese, die sich im Experiment nicht bewährt hat und nie in den Katalog aufgenommen wurde.
*   **`deprecated`**: Eine Practice, die ehemals `adopted` war, aber durch neue Evidenz, Tools oder bessere Alternativen abgelöst wurde. Deprecated Practices verbleiben als Historie im Katalog, erhalten aber ein Status-Update und werden aus den generierten Exports entfernt.

## Phasenmodell der Architektur
Um nicht an vorzeitiger Komplexität zu scheitern, gliedert sich der Aufbau in drei Phasen:

### A. Minimaler Kern (MVP)
*Zwingend erforderlich, um den Erkenntniskreislauf zu starten.*
*   **Intake:** GitHub Issues als primäre Einlassschleuse.
*   **Experiment-Engine:** `experiments/` Ordner mit vollständigem Skelett (Manifest, Methode, Evidenz, Entscheidung).
*   **Minimaler Katalog:** `catalog/` für erste `adopted` Practices.
*   **Schema-Validierung:** Harte CI-Prüfung der Kernartefakte (`schemas/`).
*   **Promotion-Gate:** Zwingender PR-Prozess für Änderungen am Katalog.
*   **Schema-Starter-Set:** Zum MVP gehört zwingend ein minimales Set real nutzbarer, durchsetzbarer Schemas (für Catalog, Experiment und Combo).
*   **Operatives Onboarding:** README und CONTRIBUTING sind als systemkritische Architekturbestandteile definiert (Ziel: Einstieg < 10 Minuten, klares Verständnis der Beitragsarten und Abläufe).

### B. Starter Corpus (Initialbefüllung)
*Direkt im Anschluss an den MVP erfolgt eine gezielte Erstbefüllung, um das System operativ nutzbar zu machen.*
*   **Initiale Katalogeinträge:** Befüllung aller Hauptkategorien.
*   **Erste Anti-Patterns:** Aktive Erfassung verworfener Ansätze als First-Class-Lerninstrumente.
*   **Erste Benchmark-Challenges:** Standardisierte Aufgaben für den methodischen Vergleich.
*   **Referenzexperiment (Golden Example):** Mindestens ein vollständig durchgeführtes Referenzexperiment zur qualitativen Orientierung.
*   **Menschenlesbare Prompts (optional):** Erste Prompt-Adaptionen (nicht kanonisch).

### C. Frühe Verstärker
*Sinnvoll nach Stabilisierung des MVPs, erhöht die Systemqualität maßgeblich.*
*   **Instruction Blocks (IR) & Exports:** Einführung von `instruction-blocks/` und automatisierte Generierung der `exports/`.
*   **Benchmarks & Observability:** Erste Heuristiken zur Erfolgsmessung sowie saubere Evidenz-Logs.
*   **Erweiterte Governance:** Feinere CODEOWNERS-Regeln und verfeinerte Status Checks.

### D. Spätphase / Optionale Schicht
*Erstrebenswert für Distribution und Skalierung im Ökosystem.*
*   **Playbooks & Onboarding:** Strukturierte `docs/` mit Triage-Runbooks.
*   **Breitere Tool-Abdeckung:** Exports für weitere Agentensysteme.
*   **Erweiterte Metriken:** Automatisierte Erfassung quantitativer Daten.

## Kanonische Artefakte
Die Pipeline stützt sich auf harte, schemavalidierte Artefaktarten:

1.  **Hypothese (Innovation)**: Problem, Hypothese, Erfolgskriterium, Scope. Formuliert als Issue-Formular.
2.  **Experiment**: Isolierter Ordner (`manifest.yml`, `method.md`, `results/result.md`, `results/decision.yml`, `results/evidence.jsonl`, `artifacts/`). Dieser Aufbau zwingt zu einem überprüfbaren Prozess statt bloßem Basteln.
    *   **Golden Examples:** Das Repository enthält zwingend mindestens ein vollständig ausgefülltes Referenzexperiment (Golden Example), um Verständnis zu erleichtern, Qualität zu standardisieren und Contributors Orientierung zu geben.
3.  **Decision Artifact (Meta-Entscheidung)**: Steuert das System selbst. Dokumentiert Metriken, Gate-Regeln, Re-/De-Katalogisierungen und Export-Ziele. Diese leben explizit im Ordner `decisions/` und entstehen immer dann, wenn Regeln, Metriken, Gates, Katalogstatus oder Export-Ziele des Systems selbst geändert, bestätigt oder außer Kraft gesetzt werden.
4.  **Catalog Entry (Practice / Anti-Pattern)**: Kuratierter Eintrag mit Status und Evidenz, verlinkt zwingend auf Experimente. Umfasst zwingend Metadaten wie `status`, `evidence_level`, `linked_experiments`, `last_tested`, `tools` und `owner`.
    *   **Anti-Patterns als First-Class-Komponente:** Anti-Patterns sind kein Nebenprodukt, sondern werden aktiv als Erstbefüllung und zentrales Lerninstrument genutzt und gepflegt.
5.  **Combo**: Unterart des Katalogs (`catalog/combos/`). Getestete Synergien/Anti-Synergien (z.B. Stil + Tool).
6.  **Benchmarks**: Definition von Metriken (Time-to-Running, Rework-Zyklen). *Wichtig:* Dies sind Startheuristiken. Qualitative Begleitevaluierung bleibt essenziell, das System darf nicht ausschließlich auf das Messbare optimieren.
    *   **Benchmark-Challenges:** Benchmarks umfassen nicht nur Metriken, sondern standardisierte, versionierte, wiederverwendbare Aufgaben ("Challenges"). Sie ermöglichen reproduzierbare Vergleiche zwischen Tools, Stilen und Workflows.
    *   **Erweiterte Bewertungsdimensionen (optional):** Neben Kernmetriken existiert ein nicht-verpflichtender Satz qualitativer Dimensionen (Geschwindigkeit, Treffsicherheit, Codequalität, Iterationsfähigkeit, kognitive Last, Skalierbarkeit, Kreativität), der die Evaluierung ergänzt.
7.  **Instruction Block IR + Exports**: Engine-neutrale Repräsentation (IR), aus der spezifische Ziel-Artefakte generiert werden.

### Die drei Regulationsebenen
Zur Vermeidung von Drift sind drei Ebenen funktional strikt getrennt:
*   **`.vibe/`**: Operative Default-Verträge dieses spezifischen Repositories (Constraints, Quality Gates).
*   **`instruction-blocks/`**: Die kanonische, wiederverwendbare Zwischenrepräsentation (IR) von Instruktionen.
*   **`exports/`**: Die daraus generierten, tool-spezifischen Ziel-Artefakte (z.B. `.cursor/rules/`, `.github/copilot-instructions.md`).
*   **Regel für generierte Artefakte:** Generierte Artefakte (wie `exports/`, `.cursor/rules/` oder `AGENTS.md`) werden **niemals manuell editiert**. Maßgeblich ist ausschließlich die IR (`instruction-blocks/`).

## Workflow: Intake bis Export

### 1. Intake: Issue-First
Die primäre Intake-Logik ist **Issue-first**.
Ein YAML-basiertes Issue Form (`.github/ISSUE_TEMPLATE/idea.yml`) erfasst die Hypothese niedrigschwellig. Erst beim Übergang in den Status `testing` erfolgt die Materialisierung als Datei/Ordner im Repository (`experiments/`).

### 2. Experiment-Durchführung
Jedes Experiment materialisiert sich als Ordner (z.B. `experiments/2026-04-08_spec-first-vs-yolo/`) basierend auf einem strikten Golden Skeleton:
*   `manifest.yml` (Setup, Hypothese, Metriken)
*   `method.md` (Ablauf und Variablen)
*   `results/result.md` (Zusammenfassung)
*   `results/decision.yml` (Adopt, Reject, Iterate; inkl. Rationale)
*   `results/evidence.jsonl` (Rohereignisse)
*   `artifacts/` (Erzeugte Diffs/Outputs)

### 3. Katalogisierung (Promotion-PR)
Die Aufnahme in den `catalog/` erfolgt ausschließlich über einen "Promotion-PR".
Dieser Gate prüft hart:
*   Existiert ein vollständiges Experiment (inkl. `evidence.jsonl`)?
*   Sind Frontmatter/Schemas im Katalog-Eintrag valide?
*   Sind Export-Artefakte synchron?
*   Passieren die Quality Gates?

### 4. Generierung der Exports & Observability
Bei Änderungen an der IR (`instruction-blocks/`) zwingt die CI zur Synchronisation der `exports/`.
Gleichzeitig bilden `evidence.jsonl`, Benchmarks, Decision Artifacts und dieser Export-Sync gemeinsam die explizite **Observability-Schicht** des Repositories.

## Governance, Zonenmodell und Contribution Contract
Sicherheit und Qualitätsschranken sind architektonisch in zwei strikte Zonen unterteilt:

*   **Labor-Schicht (Freies Explorieren):** Umfasst den Issue-Intake und den `experiments/` Pfad. Hier warnt die CI bei Schema-Fehlern nur.
*   **Bibliotheks-Schicht (Harte Validierung):** Umfasst `catalog/`, `benchmarks/`, `exports/`, `prompts/` und `decisions/`. Hier gelten strikte Review-Pflichten via `CODEOWNERS` und blockierende CI-Checks.

**Contribution Contract (Beitragsregeln):**
Zur Vermeidung von Wildwuchs definiert das System eine strikte Typisierung von Pull Requests. Jeder Beitrag muss einem Typ mit eigenen Qualitätsanforderungen zugeordnet sein (Typisierung via Label-System):
*   `Katalogeintrag`
*   `Experiment`
*   `Combo`
*   `Innovation`
*   `Prompt` (optional)

**Agenten- und Tool-Security:**
*   Lokale Agenten (z.B. Cursor) und Cloud-Agenten (z.B. Copilot) weisen unterschiedliche Reproduzierbarkeits- und Sicherheitsbedarfe auf, die in den Experiments explizit zu trennen sind.
*   MCP-basierte Integrationen unterliegen explizit strikten Consent-, Privacy- und Tool-Safety-Regeln, bevor sie als `adopted` gelten können.
*   Sicherheits-Baselines (Dependabot, Secret Scanning, Scorecard) sichern das gesamte Repository ab.

## Vorgeschlagene Zielstruktur
*Die Struktur zeigt das Zielbild, wird aber inkrementell besiedelt.*

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

  decisions/              # Meta-Entscheidungen (Systemsteuerung)
    catalog-updates/
    system-rules/

  experiments/            # Labor-Schicht: Materialisierte Testläufe
    _template/
      manifest.yml
      method.md
      results/
        decision.yml
        result.md
        evidence.jsonl
      artifacts/
    2026-04-08_spec-first/

  catalog/                # Bibliothek: Validiertes Wissen
    styles/
    technologies/
    techniques/
    workflows/
    anti-patterns/        # Wertvolles Wissen über das, was nicht funktioniert
    combos/               # Kuratierte Synergien

  prompts/                # Bibliothek: Menschenlesbare Artefakte
    adopted/

  benchmarks/             # Bibliothek: Startheuristiken & Observability
    criteria.md

  instruction-blocks/     # Bibliothek: Kanonische IR
    spec-first-vibe.yml

  exports/                # Bibliothek: Tool-spezifische Ziele (Generiert)
    copilot/
    cursor/

  schemas/                # Bibliothek: Datenmodelle für CI-Checks
    experiment.manifest.schema.json
    catalog.entry.schema.json

  docs/                   # Optionale Spätphase
    playbooks/
    onboarding/

  tools/                  # CLI / Automatisierung
    validate/
```

---

## CHANGELOG
- **Phasenmodell erweitert:** Phase B "Starter Corpus (Initialbefüllung)" als eigene klar abgegrenzte Schicht direkt nach dem MVP eingefügt.
- **Kanonische Artefakte ergänzt:**
  - *Schema-Starter-Set* sowie operative Bedeutung von *README & CONTRIBUTING* bei Phase A ergänzt.
  - *Golden Examples* unter Punkt 2 (Experiment) als referenzbildendes Muster verankert.
  - *Anti-Patterns* unter Punkt 4 als aktiv zu nutzende First-Class-Komponenten gestärkt.
  - *Benchmark-Challenges* und *Erweiterte Bewertungsdimensionen* (Geschwindigkeit, Codequalität etc.) in Punkt 6 (Benchmarks) als standardisierende Elemente eingebaut.
- **Governance erweitert:** *Contribution Contract* eingefügt, der Beiträge zwingend in PR-Typen klassifiziert (Katalogeintrag, Experiment, Combo, Innovation, Prompt) und jeweils eigene Qualitätsanforderungen auferlegt.
