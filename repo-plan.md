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
Um nicht an vorzeitiger Komplexität zu scheitern, gliedert sich der Aufbau in drei Phasen, ergänzt um eine explizite Erstbefüllungsschicht. *Die neue "Intelligence Layer" (Agentensteuerung, Dokumentsemantik) wird schrittweise über diese Phasen integriert.*

### A. Minimaler Kern (MVP)
*Zwingend erforderlich, um den Erkenntniskreislauf zu starten.*
*   **Intake:** GitHub Issues als primäre Einlassschleuse.
*   **Experiment-Engine:** `experiments/` Ordner mit vollständigem Skelett (Manifest, Methode, Evidenz, Entscheidung).
*   **Minimaler Katalog:** `catalog/` für erste `adopted` Practices.
*   **Schema-Validierung:** Harte CI-Prüfung der Kernartefakte (`schemas/`).
*   **Promotion-Gate:** Zwingender PR-Prozess für Änderungen am Katalog.
*   **Schema-Starter-Set:** Zum MVP gehört ein minimales Set real nutzbarer Schemas für Katalogeinträge, Experimente und Combos (`contracts/docmeta.schema.json`).
*   **Operatives Einstiegssystem:** `README.md` und `CONTRIBUTING.md` sind keine Beiwerk-Dateien, sondern operative Systemkomponenten. Ziel ist es, dass neue Contributors das Repo-Ziel, die Beitragstypen und den Ablauf in kürzester Zeit verstehen.
*   **Intelligence Layer (Basis):** Einführung von `repo.meta.yaml` als maschinenlesbare Verfassung, `AGENTS.md` und `agent-policy.yaml` zur Agentenführung, sowie Basis-Diagnosegeneratoren (`doc-index`).

### B. Starter Corpus (Initialbefüllung)
*Direkt im Anschluss an den MVP erfolgt eine gezielte Erstbefüllung, um das System operativ nutzbar und testbar zu machen. Dies umfasst:*
*   **Initiale Katalogeinträge:** Mindestens ein Eintrag je Hauptkategorie.
*   **Erste Anti-Patterns:** Aktive Erfassung von Mustern, die nicht funktionieren.
*   **Erste Benchmark-Challenges:** Definition standardisierter Vergleichsaufgaben.
*   **Golden Example:** Mindestens ein vollständig durchgeführtes Referenzexperiment.
*   **Adopted Prompts:** Erste menschenlesbare Prompt-Adaptionen.

### C. Frühe Verstärker
*Sinnvoll nach Stabilisierung des MVPs, erhöht die Systemqualität maßgeblich.*
*   **Instruction Blocks (IR) & Exports:** Einführung von `instruction-blocks/` und automatisierte Generierung der `exports/`.
*   **Benchmarks & Observability:** Erste Heuristiken zur Erfolgsmessung sowie saubere Evidenz-Logs.
*   **Erweiterte Governance:** Feinere CODEOWNERS-Regeln und verfeinerte Status Checks.
*   **Intelligence Layer (Ausbau):** Zusätzliche Dokument-Schemas, erweiterte Relationslogik und Generatoren für `weak-links`.

### D. Spätphase / Optionale Schicht
*Erstrebenswert für Distribution und Skalierung im Ökosystem.*
*   **Playbooks & Onboarding:** Strukturierte `docs/` mit Triage-Runbooks.
*   **Breitere Tool-Abdeckung:** Exports für weitere Agentensysteme.
*   **Erweiterte Metriken:** Automatisierte Erfassung quantitativer Daten.
*   **Intelligence Layer (Vollton):** Komplexe CI-Gates, breitere Diagnoseebene (`supersession-map`, `knowledge-gaps`).

## Die Intelligence Layer (Systemintelligenz)
Zusätzlich zur operativen Pipeline (`intake` → `experiments` → `catalog` → `exports`) erhält das Repository eine leichte, maschinenlesbare Diagnostik- und Steuerungsebene. Diese ersetzt die operative Pipeline nicht, sondern macht sie für Agenten navigierbar und schützt vor Drift.

### Maschinenlesbare Repo-Verfassung
Das Repository besitzt eine maschinenlesbare Verfassung in Form der `repo.meta.yaml`.
Diese Datei fungiert als Wahrheitsarchitektur des Repos und trennt strikt zwischen Kanon, Navigation und Diagnose. Sie definiert:
*   `entrypoints` und `canonical_sources`
*   `discovery_roots` und `generated_artifacts`
*   `safe_read_paths`, `guarded_write_paths` und `forbidden_write_paths`
*   `required_checks` und `truth_model / precedence`

### Agentenführung
vibe-lab verfügt über eine explizite Agentensteuerungsschicht, bestehend aus `AGENTS.md` und `agent-policy.yaml`.
Diese Dokumente erzwingen eine bindende Lesereihenfolge, verbieten stille Interpolation bei fehlenden Daten, setzen Pfaddisziplin durch, regeln den Umgang mit generierten Dateien und erzwingen einen Abbruch bei Konflikten in kanonischen Quellen.

**Zentrale Lesereihenfolge für Agenten:**
1. `repo.meta.yaml`
2. `AGENTS.md`
3. `agent-policy.yaml`
4. Kanonische Kernquellen
5. Navigation (nur als Navigation)
6. Generierte Diagnose (nur als Diagnose)

### Dokumente als epistemische Objekte
Markdown-Dokumente sind keine bloßen Fließtexte, sondern strukturierte Erkenntnisobjekte. Ein `contracts/docmeta.schema.json` erzwingt eine Frontmatter-Pflicht für kanonische Markdown-Dateien und standardisiert Relationen (kein Link-Wildwuchs).
*   **Pflichtfelder:** `id`, `title`, `doc_type`, `status`, `canonicality`, `summary`, `epistemic_state`, `relations`, `last_reviewed`, `tags`.
*   **Standardisierte Relations-Typen:** `relates_to`, `depends_on`, `tests`, `evaluates`, `derived_from`, `contradicts`, `supports`, `supersedes`.

*(Klarstellung: `contracts/` enthält kanonische semantische und policy-nahe Schemas wie das docmeta, während `schemas/` die operativen Validierungsschemas für Pipeline-Artefakte wie Experimente und Catalog Entries enthält.)*

### Diagnostische Generatoren
vibe-lab nutzt eine kleine Menge generierter Diagnoseartefakte unter `docs/_generated/`.
**Wichtig:** Diese Artefakte sind reine *Diagnose*, keine Wahrheit. `docs/index.md` ist Navigation, keine Wahrheit. Diese generierten Artefakte dürfen **niemals manuell editiert werden**.

*   **MVP-Generatoren:** `doc-index.md`.
*   **Spätere Generatoren:** `weak-links.md`, `supersession-map.md`, `knowledge-gaps.md`.

### Epistemische Dokumentpfade
Ergänzend zur operativen Pipeline (`experiments/`, `catalog/`, etc.) organisiert der `docs/` Ordner Wissen nicht nach Themen, sondern nach seiner epistemischen Semantik:
*   `docs/concepts/` = unvalidierte Begriffe / Denkmodelle
*   `docs/experiments/` = Versuchsdesign / Hypothesen (Doku-Ebene)
*   `docs/evaluations/` = Auswertungen
*   `docs/syntheses/` = verdichtete Erkenntnisse
*   `docs/rules/` = operationalisierte Regeln
*   `docs/blueprints/` = Überführung in Repo-/Agentenpraxis
*(Diese Struktur dient als Verdichtungs- und Diagnoseebene und ersetzt nicht die ausführbaren Experimente.)*

### Minimaler Guard-/Generator-Stack
Ein Lean-Startset an Scripts unter `scripts/docmeta/` schützt das System für den MVP:
*   `validate_schema.py`
*   `generate_doc_index.py`

### Explizite Abgrenzung (Was NICHT übernommen wird)
Um Bürokratie zu vermeiden, wird bewusst verzichtet auf:
*   Volle "Weltgewebe"-Komplexität von Beginn an.
*   Eine zu große Zahl diagnostischer Artefakte in Phase A.
*   Ops-schwere Heimserver-Formalisierungen.
*   Eine radikale YAML-Primarität für absolut alle Inhalte.
*   Themenablagen ohne epistemisches Zustandsmodell.

## Kanonische Artefakte
Die Pipeline stützt sich auf harte, schemavalidierte Artefaktarten:

1.  **Hypothese (Innovation)**: Problem, Hypothese, Erfolgskriterium, Scope. Formuliert als Issue-Formular.
2.  **Experiment**: Isolierter Ordner (`manifest.yml`, `method.md`, `results/result.md`, `results/decision.yml`, `results/evidence.jsonl`, `artifacts/`). Dieser Aufbau zwingt zu einem überprüfbaren Prozess statt bloßem Basteln.
    *   **Golden Examples:** Neben Templates enthält das Repo zwingend mindestens ein vollständig ausgefülltes Referenzexperiment. Dies dient der Orientierung für Contributors, als Prüfstein für Schemas und als Referenz für die Review-Qualität.
3.  **Decision Artifact (Meta-Entscheidung)**: Steuert das System selbst. Dokumentiert Metriken, Gate-Regeln, Re-/De-Katalogisierungen und Export-Ziele. Diese leben explizit im Ordner `decisions/` und entstehen immer dann, wenn Regeln, Metriken, Gates, Katalogstatus oder Export-Ziele des Systems selbst geändert, bestätigt oder außer Kraft gesetzt werden.
4.  **Catalog Entry (Practice / Anti-Pattern)**: Kuratierter Eintrag mit Status und Evidenz, verlinkt zwingend auf Experimente. Umfasst zwingend Metadaten wie `status`, `evidence_level`, `linked_experiments`, `last_tested`, `tools` und `owner`.
    *   **Anti-Patterns als First-Class-Komponente:** Sie sind kein Nebenprodukt, sondern werden aktiv gepflegt und als Erstbefüllung sowie als zentrales Lerninstrument genutzt.
5.  **Combo**: Unterart des Katalogs (`catalog/combos/`). Getestete Synergien/Anti-Synergien (z.B. Stil + Tool).
6.  **Benchmarks**: Definition von Metriken (Time-to-Running, Rework-Zyklen). *Wichtig:* Dies sind Startheuristiken. Qualitative Begleitevaluierung bleibt essenziell, das System darf nicht ausschließlich auf das Messbare optimieren.
    *   **Benchmark-Challenges:** Benchmarks beruhen nicht nur auf Metriken, sondern auch auf standardisierten, versionierten Vergleichsaufgaben („Challenges“). Nur diese erlauben reproduzierbare Vergleiche zwischen Stilen, Tools und Workflows.
    *   **Erweiterte Bewertungsdimensionen (optional):** Neben Kernmetriken existiert ein nicht-verpflichtender Satz qualitativer Dimensionen (Geschwindigkeit, Treffsicherheit, Codequalität, Iterationsfähigkeit, kognitive Last, Skalierbarkeit, Kreativität), der die Evaluierung ergänzt.
7.  **Instruction Block IR + Exports**: Engine-neutrale Repräsentation (IR), aus der spezifische Ziel-Artefakte generiert werden.

### Die drei Regulationsebenen
Zur Vermeidung von Drift sind drei Ebenen funktional strikt getrennt:
*   **`.vibe/`**: Operative Default-Verträge dieses spezifischen Repositories (Constraints, Quality Gates).
*   **`instruction-blocks/`**: Die kanonische, wiederverwendbare Zwischenrepräsentation (IR) von Instruktionen.
*   **`exports/`**: Die daraus generierten, tool-spezifischen Ziel-Artefakte (z.B. `.cursor/rules/`, `.github/copilot-instructions.md`).
*   **Regel für generierte Artefakte:** Generierte Artefakte (wie `exports/`, `.cursor/rules/`, `AGENTS.md` oder `docs/_generated/`) werden **niemals manuell editiert**. Maßgeblich ist ausschließlich die IR bzw. die Generatoren.

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
Gleichzeitig bilden `evidence.jsonl`, Benchmarks, Decision Artifacts, die Diagnostikgeneratoren (`docs/_generated/`) und dieser Export-Sync gemeinsam die explizite **Observability-Schicht** des Repositories.

## Governance, Zonenmodell und Contribution Contract
Sicherheit und Qualitätsschranken sind architektonisch in zwei strikte Zonen unterteilt:

*   **Labor-Schicht (Freies Explorieren):** Umfasst den Issue-Intake und den `experiments/` Pfad. Hier warnt die CI bei Schema-Fehlern nur.
*   **Bibliotheks-Schicht (Harte Validierung):** Umfasst `catalog/`, `benchmarks/`, `exports/`, `prompts/`, `contracts/` und `decisions/`. Hier gelten strikte Review-Pflichten via `CODEOWNERS` und blockierende CI-Checks.

**Contribution Contract (Strukturierte Beitragslogik):**
Um Wildwuchs zu verhindern, arbeitet das Repository mit einem expliziten Contribution Contract. Jeder Beitrag muss typisiert sein (z.B. via Labels oder PR-Templates), und jeder Typ unterliegt eigenen Mindestanforderungen:
*   `Innovation`
*   `Experiment`
*   `Catalog Entry`
*   `Combo`
*   `Prompt`
*   `Decision Artifact`

**Agenten- und Tool-Security:**
*   Lokale Agenten (z.B. Cursor) und Cloud-Agenten (z.B. Copilot) weisen unterschiedliche Reproduzierbarkeits- und Sicherheitsbedarfe auf, die in den Experiments explizit zu trennen sind.
*   MCP-basierte Integrationen unterliegen explizit strikten Consent-, Privacy- und Tool-Safety-Regeln, bevor sie als `adopted` gelten können.
*   Sicherheits-Baselines (Dependabot, Secret Scanning, Scorecard) sichern das gesamte Repository ab.

## Vorgeschlagene Zielstruktur
*Die Struktur zeigt das Zielbild, wird aber inkrementell besiedelt.*

```text
vibe-lab/
  README.md
  CONTRIBUTING.md           # Operatives Einstiegssystem
  vision.md
  repo.meta.yaml            # Maschinenlesbare Repo-Verfassung
  agent-policy.yaml         # Agentensteuerung
  AGENTS.md                 # Bindende Leseregeln für Agenten

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

  contracts/              # System-Schemas (Kanonische/policy-nahe Semantik)
    docmeta.schema.json

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

  schemas/                # Bibliothek: Datenmodelle für CI-Checks (Pipeline-Validierung)
    experiment.manifest.schema.json
    catalog.entry.schema.json

  docs/                   # Epistemische Dokumentpfade
    index.md
    masterplan.md
    concepts/             # Unvalidierte Begriffe / Denkmodelle
    experiments/          # Doku-Ebene Versuchsdesign
    evaluations/          # Auswertungen
    syntheses/            # Verdichtete Erkenntnisse
    rules/                # Operationalisierte Regeln
    blueprints/           # Überführung in Praxis
    policies/
    reference/
    playbooks/            # Triage Runbooks etc.
    onboarding/
    _generated/           # Diagnose-Artefakte

  scripts/                # Minimaler Guard-/Generator-Stack
    docmeta/
      validate_schema.py
      generate_doc_index.py

  tools/                  # CLI / Automatisierung
    validate/
```

---

## CHANGELOG
- **Phasenmodell erweitert:** Phase B "Starter Corpus (Initialbefüllung)" als eigene klar abgegrenzte Schicht direkt nach dem MVP eingefügt.
- **Intelligence Layer integriert:** Neue Architekturebene eingeführt, die `repo.meta.yaml`, `AGENTS.md` und `agent-policy.yaml` als maschinenlesbare Steuerungs- und Agentenführungsebene etabliert, ohne die operative Pipeline abzulösen.
- **Dokumentsemantik und Diagnostik:** Markdown-Dateien als epistemische Objekte mit Frontmatter/Relations-Schema (`contracts/docmeta.schema.json`) definiert; `docs/_generated/` für Diagnoseartefakte und Guard-Scripts (`scripts/docmeta/`) integriert.
- **Kanonische Artefakte ergänzt:**
  - *Schema-Starter-Set* sowie operative Bedeutung von *README & CONTRIBUTING* bei Phase A ergänzt.
  - *Golden Examples* unter Punkt 2 (Experiment) als referenzbildendes Muster verankert.
  - *Anti-Patterns* unter Punkt 4 als aktiv zu nutzende First-Class-Komponenten gestärkt.
  - *Benchmark-Challenges* und *Erweiterte Bewertungsdimensionen* (Geschwindigkeit, Codequalität etc.) in Punkt 6 (Benchmarks) als standardisierende Elemente eingebaut.
- **Governance erweitert:** *Contribution Contract* eingefügt, der Beiträge zwingend in PR-Typen klassifiziert (Innovation, Experiment, Catalog Entry, Combo, Prompt, Decision Artifact) und jeweils eigene Qualitätsanforderungen auferlegt.
