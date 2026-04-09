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

Operativ durchlaufen Artefakte die Status: `idea` → `testing` → `adopted` / `rejected` → `deprecated` / `blocked` / `inconclusive`.

**Erweitertes Statusmodell:**
*   **`rejected`**: Eine Hypothese, die sich im Experiment nicht bewährt hat und nie in den Katalog aufgenommen wurde.
*   **`deprecated`**: Eine Practice, die ehemals `adopted` war, aber durch neue Evidenz, Tools oder bessere Alternativen abgelöst wurde. Deprecated Practices verbleiben als Historie im Katalog, erhalten aber ein Status-Update und werden aus den generierten Exports entfernt.
*   **`blocked`**: Operativer Status für Experimente, die aus externen Gründen pausieren (z.B. Tool-Bug, API-Release).
*   **`inconclusive`**: Epistemischer Status für Experimentläufe ohne belastbares Urteil. Zwingt zu einer expliziten, begründeten Entscheidung statt eines Schwebezustands.

## Phasenmodell der Architektur
Um nicht an vorzeitiger Komplexität zu scheitern, gliedert sich der Aufbau in drei Phasen, ergänzt um eine explizite Erstbefüllungsschicht. *Die neue "Intelligence Layer" (Agentensteuerung, Dokumentsemantik) wird schrittweise über diese Phasen integriert.*

### A. Minimaler Kern (MVP)
*Zwingend erforderlich, um den Erkenntniskreislauf zu starten.*
*   **Typed Intake:** Mindestens drei YAML Issue Forms dienen als primäre Einlassschleuse und mappen direkt auf den Contribution Contract: `idea` (für Innovationen), `experiment-proposal` (für Experimente), `promotion-request` (für Catalog Entries, Prompts, Combos).
*   **Experiment-Engine:** `experiments/` Ordner mit vollständigem Skelett (Manifest, Methode, Evidenz, Entscheidung). Iterationen müssen über Felder wie `replicated_from` oder `parent_experiment` verlinkt sein (Experiment-Chaining).
*   **Evidenz-Taxonomie:** `evidence.jsonl` nutzt ein maschinenlesbares, fixes Vokabular (`event_type`: z.B. `rework_cycle`, `token_usage`, `manual_intervention`) und wird via JSON-Schema validiert.
*   **Minimaler Katalog:** `catalog/` für erste `adopted` Practices.
*   **Schema-Validierung & Versionierung:** Harte CI-Prüfung der Kernartefakte. Alle schemavalidierten Artefakte erfordern ein `schema_version` Feld in ihrem Frontmatter oder Root-Node. Brechende Schema-Änderungen erzwingen eine Migrationsnotiz via Decision-Artifact.
*   **Promotion-Gate:** Zwingender PR-Prozess für Änderungen am Katalog.
*   **Scaffolding-CLI (Make-Frontdoor):** Ein minimales CLI (`tools/vibe-cli` oder `make vibe`) stellt Befehle wie `new experiment`, `new catalog-entry` bereit, um Boilerplate zu reduzieren.
*   **Schema-Starter-Set:** Zum MVP gehört ein minimales Set real nutzbarer Schemas für Katalogeinträge, Experimente und Combos.
*   **Operatives Einstiegssystem:** `README.md` und `CONTRIBUTING.md` sind keine Beiwerk-Dateien, sondern operative Systemkomponenten. Ziel ist es, dass neue Contributors das Repo-Ziel, die Beitragstypen und den Ablauf in kürzester Zeit verstehen.
*   **Intelligence Layer (Basis):** Einführung von `repo.meta.yaml` als maschinenlesbare Verfassung, `AGENTS.md` und `agent-policy.yaml` zur Agentenführung, sowie Basis-Diagnosegeneratoren (`doc-index`).

### B. Starter Corpus (Initialbefüllung)
*Direkt im Anschluss an den MVP erfolgt eine gezielte Erstbefüllung, um das System operativ nutzbar und testbar zu machen. Dies umfasst:*
*   **Initiale Katalogeinträge:** Mindestens ein Eintrag je Hauptkategorie.
*   **Erste Anti-Patterns:** Aktive Erfassung von Mustern, die nicht funktionieren.
*   **Erste Benchmark-Challenges:** Definition standardisierter Vergleichsaufgaben.
*   **Golden Example:** Mindestens ein vollständig durchgeführtes Referenzexperiment (inkl. zwingendem `CONTEXT.md` / `INITIAL.md` zur Reproduzierbarkeit). *Dieses reproduzierbare Kontext-Engineering ist Pflicht für alle Kandidaten, die `adopted` werden sollen.*
*   **Adopted Prompts:** Erste menschenlesbare Prompt-Adaptionen.

### C. Frühe Verstärker
*Sinnvoll nach Stabilisierung des MVPs, erhöht die Systemqualität maßgeblich.*
*   **Instruction Blocks (IR) & Exports:** Einführung von `instruction-blocks/` und automatisierte Generierung der `exports/`. Inklusive **Export-Konflikt-Gate** (harter Build-Fail bei Kollision) und **Export-Orphan-Check** (verhindert Zombie-Exporte).
    *   *Export-Herkunft:* Generierte Exporte enthalten maschinenlesbare Metadaten (`generated_from`, Hash, Generator-Version, Timestamp).
*   **Wissensverfall (Staleness):** Re-Validierung als Lifecycle-Mechanik. Katalogeinträge erhalten `last_validated`, `review_cycle` und `next_review_due`. Ein Generator (`stale-entries.md`) dient als Wartungssignal.
*   **Leichtgewichtiges Metrik-Dashboard:** Ein Generator leitet Trends aus `evidence.jsonl` ab und legt diese unter `docs/_generated/metrics/` ab.
*   **Frühe Diagnose-Kopplung:** Generatoren wie `weak-links` und `knowledge-gaps` werden an das Staleness-Signal gekoppelt, um automatisch Innovation-/Experiment-Issues zu triggern.
*   **Typisierte Decision Artifacts:** Differenzierung in Ordner wie `decisions/process/`, `decisions/export/` und `decisions/policy/`.
*   **Benchmark-Challenge Versionierung:** Versionierte Challenges (z.B. `rest-api-v1.md`). Ein zwingendes `challenge_version` Feld in `results/decision.yml` (oder dem Benchmark-Result-Schema) sorgt für Stabilität über die Zeit.
*   **Erweiterte Governance (Rulesets):** Nutzung von GitHub Rulesets zur feineren, pfadbasierten Durchsetzung des Zonenmodells (Labor vs. Bibliothek).

### D. Spätphase / Optionale Schicht
*Erstrebenswert für Distribution und Skalierung im Ökosystem.*
*   **Playbooks & Onboarding:** Strukturierte `docs/` mit Triage-Runbooks.
*   **Breitere Tool-Abdeckung:** Exports für weitere Agentensysteme.
*   **Erweiterte Metriken:** Automatisierte Erfassung quantitativer Daten.
*   **Intelligence Layer (Vollton):** Komplexe CI-Gates, breitere Diagnoseebene (`supersession-map`, `knowledge-gaps`).
*   **Reaktiver Loop (Minimal-Implementierung):** Einführung eines ersten emergenten Kreislaufs (1 State, 1 Signal, 1 Policy, 1 Action, 1 Evaluation), um erstes reaktives Verhalten zu testen, ohne das System zu überladen.
    *   *Konkretes End-to-End-Beispiel:* State (`catalog_entry` stale) → Signal (staleness) → Policy (request_revalidation) → Action (open_issue) → Evaluation (resolved/ignored) → State.
*   **Zusätzliche späte Hebel:**
    *   **AI-gestütztes Onboarding:** Ein optionaler MCP-Bot für geführte Contributor-Flows.
    *   **Trigger-Mechanismen:** Präzisierung der reaktiven Trigger (z.B. GitHub Actions vs. lokale Hooks).
    *   **Staleness/Retention-Strategie:** Archivierungsregeln (z.B. `experiments/_archive/`), um die aktive Fläche klein zu halten.
    *   **Repo-Viability Check:** Eine weiche, quartalsweise Governance-Review (ggf. "Scope zurückbauen"), statt eines harten Kill-Switches.

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

**Konzeptionelles Agentenmodell:**
Agenten können im System funktional unterschieden werden: *Sensor* (erfasst State), *Interpreter* (deutet Signal), *Policy* (trifft Entscheidung), *Executor* (führt Action aus) und *Critic* (übernimmt Evaluation). Dies dient als reines Denkmodell, ohne neue Ordnerstrukturen zu erzwingen.

### Reaktive Steuerlogik (Emergente Erweiterung)
Das System soll perspektivisch Zustände nicht nur speichern, sondern interpretieren und darauf reagieren. Dazu wird ein konzeptioneller Kreislauf eingeführt:
**STATE → SIGNAL → POLICY → ACTION → EVALUATION → STATE**

*   **State:** Beobachtbarer Zustand (z.B. Drift, fehlende Links).
*   **Signal:** Interpretierte Bedeutung („Spannung“).
*   **Policy:** Deklarative Regel („wenn X, dann Y unter Constraints Z“). Policies fungieren nicht nur als Constraints, sondern als reaktive Entscheidungslogik, die Diagnose mit Handlung verbindet.
*   **Action:** Konkrete Ausführung (untergeordnet).
*   **Evaluation:** Bewertung und Rückführung ins System.
*(Klarstellung: Manuelle Commands bleiben erhalten, werden aber durch Policies gesteuert und perspektivisch weniger direkt durch Benutzer oder Agenten initiiert.)*

### Dokumente als epistemische Objekte
Markdown-Dokumente sind keine bloßen Fließtexte, sondern strukturierte Erkenntnisobjekte. Ein `contracts/docmeta.schema.json` erzwingt eine Frontmatter-Pflicht für kanonische Markdown-Dateien und standardisiert Relationen (kein Link-Wildwuchs).
*   **Pflichtfelder:** `id`, `title`, `doc_type`, `status`, `canonicality`, `summary`, `epistemic_state`, `relations`, `last_reviewed`, `tags`.
*   **Standardisierte Relations-Typen:** `relates_to`, `depends_on`, `tests`, `evaluates`, `derived_from`, `contradicts`, `supports`, `supersedes`.

*(Klarstellung: `contracts/` enthält kanonische semantische und policy-nahe Schemas wie das docmeta, während `schemas/` die operativen Validierungsschemas für Pipeline-Artefakte wie Experimente und Catalog Entries enthält.)*

### Diagnostische Generatoren
vibe-lab nutzt eine kleine Menge generierter Diagnoseartefakte unter `docs/_generated/`.
**Wichtig:** Diese Artefakte sind reine *Diagnose*, keine Wahrheit. `docs/index.md` ist Navigation, keine Wahrheit. Diese generierten Artefakte dürfen **niemals manuell editiert werden**.

*   **MVP-Generatoren:** `doc-index.md`.
*   **Phase C/D Generatoren:** `stale-entries.md`, `weak-links.md`, `supersession-map.md`, `knowledge-gaps.md`.

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

*(Für Phase C/D werden hier schrittweise Generatoren wie `generate_stale_entries.py`, `generate_weak_links.py` etc. ergänzt.)*

### Explizite Abgrenzung (Was NICHT übernommen wird)
Um Bürokratie zu vermeiden, wird bewusst verzichtet auf:
*   Volle "Weltgewebe"-Komplexität von Beginn an.
*   Eine zu große Zahl diagnostischer Artefakte in Phase A.
*   Ops-schwere Heimserver-Formalisierungen.
*   Eine radikale YAML-Primarität für absolut alle Inhalte.
*   Themenablagen ohne epistemisches Zustandsmodell.
*   Generator-Explosionen ohne entsprechendes Wartungsbudget.

## Kanonische Artefakte
Die Pipeline stützt sich auf harte, schemavalidierte Artefaktarten:

1.  **Hypothese (Innovation)**: Problem, Hypothese, Erfolgskriterium, Scope. Formuliert als Issue-Formular.
2.  **Experiment**: Isolierter Ordner (`manifest.yml`, `method.md`, `results/result.md`, `results/decision.yml`, `results/evidence.jsonl`, `artifacts/`). Dieser Aufbau zwingt zu einem überprüfbaren Prozess statt bloßem Basteln. `manifest.yml` benötigt zwingend ein `schema_version` Feld.
    *   **Golden Examples:** Neben Templates enthält das Repo zwingend mindestens ein vollständig ausgefülltes Referenzexperiment (inkl. `CONTEXT.md` / `INITIAL.md`). Dies dient der Orientierung für Contributors, als Prüfstein für Schemas und als Referenz für die Review-Qualität.
3.  **Decision Artifact (Meta-Entscheidung)**: Steuert das System selbst. Dokumentiert Metriken, Gate-Regeln, Re-/De-Katalogisierungen und Export-Ziele. Diese leben explizit im Ordner `decisions/` und entstehen immer dann, wenn Regeln, Metriken, Gates, Katalogstatus oder Export-Ziele des Systems selbst geändert, bestätigt oder außer Kraft gesetzt werden. Sie werden typisiert (z.B. `decisions/process/`, `decisions/policy/`).
4.  **Catalog Entry (Practice / Anti-Pattern)**: Kuratierter Eintrag mit Status und Evidenz, verlinkt zwingend auf Experimente. Umfasst zwingend Metadaten wie `status`, `evidence_level`, `linked_experiments`, `last_validated`, `review_cycle`, `next_review_due`, `tools` und `owner`, sowie ein `schema_version` Feld.
    *   **Anti-Patterns als First-Class-Komponente:** Sie sind kein Nebenprodukt, sondern werden aktiv gepflegt und als Erstbefüllung sowie als zentrales Lerninstrument genutzt. Sie nutzen eine standardisierte Taxonomie (z.B. `too_fragile`, `not_reproducible`, `tool_lock_in`, `security_risk`).
5.  **Combo**: Unterart des Katalogs (`catalog/combos/`). Getestete Synergien/Anti-Synergien (z.B. Stil + Tool).
6.  **Benchmarks**: Definition von Metriken (Time-to-Running, Rework-Zyklen). *Wichtig:* Dies sind Startheuristiken. Qualitative Begleitevaluierung bleibt essenziell, das System darf nicht ausschließlich auf das Messbare optimieren.
    *   **Benchmark-Challenges:** Benchmarks beruhen nicht nur auf Metriken, sondern auch auf standardisierten, versionierten Vergleichsaufgaben („Challenges“). Nur diese erlauben reproduzierbare Vergleiche zwischen Stilen, Tools und Workflows.
    *   **Erweiterte Bewertungsdimensionen (optional):** Neben Kernmetriken existiert ein nicht-verpflichtender Satz qualitativer Dimensionen (Geschwindigkeit, Treffsicherheit, Codequalität, Iterationsfähigkeit, kognitive Last, Skalierbarkeit, Kreativität), der die Evaluierung ergänzt.
7.  **Instruction Block IR + Exports**: Engine-neutrale Repräsentation (IR), aus der spezifische Ziel-Artefakte generiert werden. (Exporte erfordern Herkunftsmetadaten wie `generated_from`, Hashes und die Generator-Version).

### Die drei Regulationsebenen
Zur Vermeidung von Drift sind drei Ebenen funktional strikt getrennt:
*   **`.vibe/`**: Operative Default-Verträge dieses spezifischen Repositories (Constraints, Quality Gates).
*   **`instruction-blocks/`**: Die kanonische, wiederverwendbare Zwischenrepräsentation (IR) von Instruktionen.
*   **`exports/`**: Die daraus generierten, tool-spezifischen Ziel-Artefakte (z.B. `.cursor/rules/`, `.github/copilot-instructions.md`).
*   **Regel für generierte Artefakte:** Generierte Artefakte (wie `exports/`, `.cursor/rules/`, `AGENTS.md` oder `docs/_generated/`) werden **niemals manuell editiert**. Maßgeblich ist ausschließlich die IR bzw. die Generatoren.

## Workflow: Intake bis Export

### 1. Intake: Issue-First
Die primäre Intake-Logik ist **Issue-first** (via typisierte YAML Issue Forms).
Ein YAML-basiertes Issue Form (`.github/ISSUE_TEMPLATE/idea.yml`) erfasst die Hypothese niedrigschwellig. Erst beim Übergang in den Status `testing` erfolgt die Materialisierung als Datei/Ordner im Repository (`experiments/`). Die Forms mappen sauber auf den Contribution Contract (`idea` → Innovation, `experiment-proposal` → Experiment, `promotion-request` → Catalog Entry/Combo/Prompt).

### 2. Experiment-Durchführung
Jedes Experiment materialisiert sich als Ordner (z.B. `experiments/2026-04-08_spec-first-vs-yolo/`) basierend auf einem strikten Golden Skeleton:
*   `manifest.yml` (Setup, Hypothese, Metriken, `schema_version`, `replicated_from`)
*   `method.md` (Ablauf und Variablen)
*   `results/result.md` (Zusammenfassung)
*   `results/decision.yml` (Adopt, Reject, Iterate; inkl. Rationale und `challenge_version`)
*   `results/evidence.jsonl` (Rohereignisse mit fixem Vokabular)
*   `artifacts/` (Erzeugte Diffs/Outputs)

### 3. Katalogisierung (Promotion-PR)
Die Aufnahme in den `catalog/` erfolgt ausschließlich über einen "Promotion-PR".
Dieser Gate prüft hart:
*   Existiert ein vollständiges Experiment (inkl. `evidence.jsonl`)?
*   Sind Frontmatter/Schemas im Katalog-Eintrag valide? (Inklusive obligatorischem `CONTEXT.md`/`INITIAL.md` zur Reproduzierbarkeit).
*   Sind Export-Artefakte synchron?
*   Passieren die Quality Gates?

### 4. Generierung der Exports & Observability
Bei Änderungen an der IR (`instruction-blocks/`) zwingt die CI zur Synchronisation der `exports/`.
Gleichzeitig bilden `evidence.jsonl`, Benchmarks, Decision Artifacts, die Diagnostikgeneratoren (`docs/_generated/`) und dieser Export-Sync gemeinsam die explizite **Observability-Schicht** des Repositories.

## Governance, Zonenmodell und Contribution Contract
Sicherheit und Qualitätsschranken sind architektonisch in zwei strikte Zonen unterteilt:

*   **Labor-Schicht (Freies Explorieren):** Umfasst den Issue-Intake und den `experiments/` Pfad. Hier warnt die CI bei Schema-Fehlern nur.
*   **Bibliotheks-Schicht (Harte Validierung):** Umfasst `catalog/`, `benchmarks/`, `exports/`, `prompts/`, `contracts/` und `decisions/`. Hier gelten strikte Review-Pflichten via `CODEOWNERS` (und perspektivisch GitHub Rulesets) sowie blockierende CI-Checks.

**Contribution Contract (Strukturierte Beitragslogik):**
Um Wildwuchs zu verhindern, arbeitet das Repository mit einem expliziten Contribution Contract. Jeder Beitrag muss typisiert sein (z.B. via Labels oder PR-Templates, passend zu den Intake Issue Forms), und jeder Typ unterliegt eigenen Mindestanforderungen:
*   `Innovation` (gemappt von `idea`)
*   `Experiment` (gemappt von `experiment-proposal`)
*   `Catalog Entry` (gemappt von `promotion-request`)
*   `Combo`
*   `Prompt`
*   `Decision Artifact`

**Traceability (Pflicht für Reaktivität):**
Um Emergenz kontrollierbar und debugbar zu halten, muss jede automatisch (reaktiv) ausgelöste Aktion strikt nachvollziehbar dokumentiert werden. Beispielstruktur:
```yaml
trace:
  triggered_by: <signal>
  policy: <policy_id>
  action: <action_id>
  outcome: <result>
```

**Agenten- und Tool-Security:**
*   Lokale Agenten (z.B. Cursor) und Cloud-Agenten (z.B. Copilot) weisen unterschiedliche Reproduzierbarkeits- und Sicherheitsbedarfe auf, die in den Experiments explizit zu trennen sind.
*   MCP-basierte Integrationen unterliegen explizit strikten Consent-, Privacy- und Tool-Safety-Regeln, bevor sie als `adopted` gelten können.
*   **Secret- / Konfigurationsverwaltung:** Es gelten verbindliche Repo-Regeln (`.env.example`, `.gitignore`-Konventionen, explizites "no secrets in commits"), durchgesetzt via Push Protection und Secret Scanning.
*   **Privacy- / Ethik-Policy:** In `evidence.jsonl` und Artefakten sind keine personenbezogenen Daten oder Secret-Material erlaubt (inkl. Redaction-Regeln und Agent-Policy-Enforcement). Diese Regeln sind unter `docs/policies/privacy-and-ethics.md` kodifiziert.
*   **Prompt-Injection-Härtung:** Für `exports/` gilt ein striktes Sanitization-Prinzip (keine untrusted User-Strings in Exports ohne Filter) als dedizierter Security-Review-Schritt.

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
      idea.yml            # Typed Intake (Innovation)
      experiment-proposal.yml # Typed Intake (Experiment)
      promotion-request.yml   # Typed Intake (Catalog/Combo/Prompt)
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
    process/              # Prozess-Retrospektiven
    export/
    policy/
    benchmark/

  experiments/            # Labor-Schicht: Materialisierte Testläufe
    _archive/             # Staleness/Retention
    _template/
      manifest.yml
      method.md
      results/
        decision.yml
        result.md
        evidence.jsonl    # Maschinenlesbare Evidenz-Taxonomie
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
    challenges/           # Versionierte Vergleichsaufgaben
      rest-api-v1.md

  instruction-blocks/     # Bibliothek: Kanonische IR
    spec-first-vibe.yml

  exports/                # Bibliothek: Tool-spezifische Ziele (Generiert)
    copilot/
    cursor/

  schemas/                # Bibliothek: Datenmodelle für CI-Checks (Pipeline-Validierung)
    experiment.manifest.schema.json
    catalog.entry.schema.json
    combo.schema.json

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
      privacy-and-ethics.md
    reference/
    playbooks/            # Triage Runbooks etc.
    onboarding/
    _generated/           # Diagnose-Artefakte
      metrics/            # Leichtgewichtiges Metrik-Dashboard
      stale-entries.md    # Phase C Generator-Output
      weak-links.md       # Phase C/D Generator-Output

  scripts/                # Minimaler Guard-/Generator-Stack
    docmeta/
      validate_schema.py
      generate_doc_index.py
      generate_stale_entries.py # Phase C/D Erweiterung
      generate_weak_links.py    # Phase C/D Erweiterung

  tools/                  # CLI / Automatisierung
    vibe-cli/             # Scaffolding-CLI (Make-Frontdoor)
    validate/
```

---

## CHANGELOG
- **Erweiterungspläne integriert:**
  - *Phase A (MVP):* Typed Intake (Issue Forms) direkt gemappt auf Contribution Contract, Scaffolding-CLI (`tools/vibe-cli`), Secret-/Konfigurationsverwaltung (inkl. Push Protection), fixierte Evidenz-Taxonomie für `evidence.jsonl`, Status `blocked` sauber getrennt, Experiment-Chaining (`replicated_from`), Schema-Versionierung in `manifest.yml` und Catalog Entries inkl. Migrationspfad, Export-Konflikt-Gates & Orphan-Checks, sowie Prompt-Injection-Härtung speziell für `exports/`.
  - *Phase C (Frühe Verstärker):* Lifecycle-Mechaniken (Staleness/Decay mit `review_cycle`, `next_review_due` und `stale-entries.md`), leichtgewichtiges Metrik-Dashboard (`docs/_generated/metrics/`), Kopplung von Weak-Links/Knowledge-Gaps an Staleness-Signale zur automatischen Ticketgenerierung, typisierte Decision-Artifacts (`process/`, `policy/`), Context-Engineering (`CONTEXT.md`) als harte Pflicht für *alle* `adopted`-Kandidaten, Privacy-/Ethik-Policy (`docs/policies/privacy-and-ethics.md`), Benchmark-Challenge-Versionierung in `decision.yml`, Anti-Pattern-Fehlermodus-Taxonomie und GitHub Rulesets. Generatoren für Phase C/D in `scripts/docmeta/` und Ausgaben in `docs/_generated/` explizit ergänzt. Exporte enthalten nun Herkunftsmetadaten (z.B. Hash, Generator-Version).
  - *Phase D (Spätphase):* Optionale Tools wie MCP-Bot für Onboarding, Präzisierung von reaktiven Trigger-Mechanismen, Staleness-/Retention-Strategien (Archivierung) und Repo-Viability Checks.
- **Phasenmodell erweitert:** Phase B "Starter Corpus (Initialbefüllung)" als eigene klar abgegrenzte Schicht direkt nach dem MVP eingefügt. Spätphase (D) um reaktiven Minimal-Loop ergänzt (inkl. End-to-End-Beispiel).
- **Intelligence Layer integriert:** Neue Architekturebene eingeführt, die `repo.meta.yaml`, `AGENTS.md` und `agent-policy.yaml` als maschinenlesbare Steuerungs- und Agentenführungsebene etabliert, ohne die operative Pipeline abzulösen.
- **Reaktive Steuerlogik:** Ergänzung eines emergenten Kreislaufs (STATE → SIGNAL → POLICY → ACTION → EVALUATION) zur Systemsteuerung, ergänzt durch konzeptionelle Agenten-Rollen (Sensor, Interpreter, etc.) und strikte Traceability-Vorgaben für Debugbarkeit.
- **Dokumentsemantik und Diagnostik:** Markdown-Dateien als epistemische Objekte mit Frontmatter/Relations-Schema (`contracts/docmeta.schema.json`) definiert; `docs/_generated/` für Diagnoseartefakte und Guard-Scripts (`scripts/docmeta/`) integriert.
- **Governance erweitert:** *Contribution Contract* eingefügt, der Beiträge zwingend in PR-Typen klassifiziert (Innovation, Experiment, Catalog Entry, Combo, Prompt, Decision Artifact) und jeweils eigene Qualitätsanforderungen auferlegt.
- **Kohärenz-Fixes:** Schema-Starter-Set exakt mit der `schemas/`-Ordnerstruktur synchronisiert (inkl. `combo.schema.json`) und Unterscheidung zwischen `contracts/` und `schemas/` klargestellt. `CONTRIBUTING.md` als operatives System dokumentiert. `blocked` als einziger operativer Pausenstatus normiert.
