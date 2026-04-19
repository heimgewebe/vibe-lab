---
title: "Repository-Plan"
status: active
canonicality: foundational
updated: "2026-04-19"
---
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

**Erweitertes Statusmodell:**
Artefakte durchlaufen im Repository folgende strukturierten Zustände:
- [ ] **Operativer Fluss:** `idea` → `testing` → `adopted` / `rejected` (Eine Hypothese, die sich im Experiment nicht bewährt hat und nie in den Katalog aufgenommen wurde).
- [ ] **Sonderstatus:** `blocked` für pausierte Experimente, die aus externen Gründen warten (z.B. Tool-Bug, API-Release).
- [ ] **Folgestatus:** `deprecated` für eine ehemals `adopted` Practice, die durch neue Evidenz abgelöst wurde. Diese verbleibt als Historie im Katalog, erhält aber ein Status-Update und wird aus generierten Exports entfernt.
- [ ] **Entscheidungsstatus:** `inconclusive` für Experimentläufe ohne belastbares Urteil. Zwingt zu einer expliziten Entscheidung statt eines Schwebezustands.

## Phasenmodell der Architektur (Umsetzungsplan)
Um nicht an vorzeitiger Komplexität zu scheitern, gliedert sich der Aufbau strukturiert in vier Phasen (A bis D), wobei Phase B explizit der Erstbefüllung dient. *Die "Intelligence Layer" (Agentensteuerung, Dokumentsemantik) wird schrittweise über diese Phasen hinweg integriert.*

### A. Minimaler Kern (MVP)
*Zwingend erforderlich, um den Erkenntniskreislauf zu starten. (Klarstellung: Um den MVP nicht zu überladen, dürfen einzelne Bestandteile als Stub oder in einer reduzierten Erstversion starten.)*

**Umsetzungs-Checkliste Phase A:**
- [ ] **Typed Intake:** YAML Issue Forms für `idea`, `experiment-proposal` und `promotion-request` sind angelegt und auf den Contribution Contract gemappt.
- [ ] **Experiment-Engine:** Der Ordner `experiments/_template/` existiert inkl. `manifest.yml`, `method.md`, `evidence.jsonl` und `decision.yml`.
- [ ] **Evidenz-Taxonomie:** `evidence.jsonl` nutzt ein maschinenlesbares Vokabular (`event_type`) und wird via JSON-Schema validiert.
- [ ] **Minimaler Katalog:** Der Ordner `catalog/` existiert als Stub für erste Practices.
- [ ] **Schema-Starter-Set:** Ein Set real nutzbarer Schemas für Katalogeinträge, Experimente und Combos liegt in `schemas/` bzw. `contracts/` bereit.
- [ ] **Schema-Validierung & Versionierung:** CI-Checks (`.github/workflows/validate.yml`) prüfen hart gegen Schema-Definitionen (inkl. `schema_version`).
- [ ] **Promotion-Gate:** Zwingende PR-Templates (`promotion.md`) regeln den Aufstieg in den Katalog.
- [ ] **Scaffolding-CLI & Frontdoor:** Ein minimales `Makefile` (`make validate`, `make vibe`) und/oder `tools/vibe-cli` (z.B. `new experiment`) existieren, um Boilerplate zu senken.
- [ ] **Operatives Einstiegssystem:** `README.md` und `CONTRIBUTING.md` erklären Repo-Ziel, Beitragstypen und den Ablauf auf einen Blick (< 10 Minuten Lesezeit).
- [ ] **Intelligence Layer (Basis):** `repo.meta.yaml`, `AGENTS.md` und `agent-policy.yaml` existieren in erster Version. Die Basis-Navigationsdokumente `docs/index.md` und `docs/masterplan.md` sind angelegt. Die Basis-Diagnosegeneratoren (`generate_doc_index.py`, `generate_backlinks.py`, `generate_orphans.py`, `generate_system_map.py`) sowie die Validatoren (`validate_schema.py`, `validate_relations.py`) liegen ausführbar bereit. Der Generated-Artifact-Contract (`.vibe/generated-artifacts.yml`) klassifiziert alle generierten Ausgaben in `canonical`, `derived` und `ephemeral` und legt CI-Verhalten (blocking vs. non-blocking vs. artifact-only) für jede Klasse fest.

**Akzeptanzkriterien für Phase A (MVP abgeschlossen, wenn):**
- [ ] Ein Issue lässt sich über ein typisiertes YAML-Formular erstellen.
- [ ] Ein PR für ein Experiment triggert erfolgreich einen Schema-CI-Check.
- [ ] Die `AGENTS.md` und `repo.meta.yaml` sind im Root angelegt.
- [ ] `README.md` und `CONTRIBUTING.md` verweisen auf den Contribution Contract.
- [ ] Der Befehl `make validate` (oder ein Workflow) existiert und führt den minimalen Guard-Stack (Schema- und Relations-Validierung) ohne Fehler aus.
- [ ] `docs/index.md` und `docs/masterplan.md` existieren als Navigationsbasis.
- [ ] Die vier Basis-Diagnosegeneratoren (Index, Backlinks, Orphans, System-Map) sind funktional vorhanden.

### B. Starter Corpus (Initialbefüllung)
*Direkt im Anschluss an den MVP erfolgt eine gezielte Erstbefüllung, um das System operativ nutzbar und testbar zu machen.*

**Umsetzungs-Checkliste Phase B:**
- [ ] **Initiale Katalogeinträge:** Mindestens ein Eintrag pro Hauptkategorie (`styles`, `technologies`, `techniques`, `workflows`, `combos`) ist angelegt.
- [ ] **Erste Anti-Patterns:** Der Ordner `anti-patterns/` enthält mindestens ein aktiv erfasstes, verworfenes Muster.
- [ ] **Erste Benchmark-Challenges:** Standardisierte Vergleichsaufgaben sind unter `benchmarks/challenges/` definiert.
- [ ] **Golden Example:** Ein vollständig durchgeführtes Referenzexperiment (inkl. zwingendem `CONTEXT.md`/`INITIAL.md`) liegt in `experiments/` vor.
- [ ] **Adopted Prompts:** Ein erster menschenlesbarer Prompt liegt in `prompts/adopted/`.

**Akzeptanzkriterien für Phase B (Starter Corpus abgeschlossen, wenn):**
- [ ] Mindestens ein Golden Example-Experiment existiert und validiert fehlerfrei.
- [ ] Der Katalog enthält mindestens eine Adopted Practice und ein Anti-Pattern.
- [ ] Mindestens eine Benchmark-Challenge ist versioniert angelegt.
- [ ] Das System ist nicht mehr leer, und die Pipeline kann an konkreten Beispieldaten nachvollzogen werden.

### C. Frühe Verstärker
*Sinnvoll nach Stabilisierung des MVPs, erhöht die Systemqualität maßgeblich.*

**Umsetzungs-Checkliste Phase C:**
- [ ] **Instruction Blocks (IR) & Exports:** `instruction-blocks/` ist etabliert, und ein CI-Schritt generiert `exports/`.
- [ ] **Export-Konflikt-Gate & Orphan-Check:** Der Build-Prozess schlägt bei Export-Kollisionen hart fehl; ungenutzte Exporte werden erkannt.
- [ ] **Export-Herkunft:** Generierte Exporte dokumentieren maschinenlesbar ihre Herkunft (Hash, Generator, Timestamp).
- [ ] **Wissensverfall (Staleness):** Katalogeinträge nutzen `last_validated`, `review_cycle`, und `next_review_due`. Der Generator `generate_stale_entries.py` läuft.
- [ ] **Leichtgewichtiges Metrik-Dashboard:** Trends aus `evidence.jsonl` werden regelmäßig nach `docs/_generated/metrics/` exportiert.
- [ ] **Frühe Diagnose-Kopplung:** Generatoren wie `generate_weak_links.py` laufen und koppeln an das Staleness-Signal zur automatischen Ticketgenerierung.
- [ ] **Typisierte Decision Artifacts:** `decisions/` ist strukturiert nach `process/`, `export/`, `policy/`.
- [ ] **Benchmark-Challenge Versionierung:** Ergebnisse in `decision.yml` referenzieren zwingend ein `challenge_version` Feld.
- [ ] **Erweiterte Governance:** GitHub Rulesets für das Zonenmodell (Labor vs. Bibliothek) sind konfiguriert.

**Akzeptanzkriterien für Phase C (Verstärker abgeschlossen, wenn):**
- [ ] Änderungen in der IR (`instruction-blocks/`) lösen automatisiert Exporte aus.
- [ ] Veraltete Katalogeinträge werden durch `stale-entries.md` oder Issues sichtbar gemacht.
- [ ] Ein Metrik-Trend aus `evidence.jsonl` ist in `docs/_generated/metrics/` ablesbar.
- [ ] Export-Konflikte führen verlässlich zu einem abbrechenden Build.

### D. Spätphase / Optionale Schicht
*Erstrebenswert für Distribution und Skalierung im Ökosystem.*

**Umsetzungs-Checkliste Phase D:**
- [ ] **Playbooks & Onboarding:** Triage-Runbooks und Onboarding-Docs liegen in `docs/playbooks/` bzw. `docs/onboarding/`.
- [ ] **Breitere Tool-Abdeckung:** Exports unterstützen weitere Agentensysteme jenseits der Startkonfiguration.
- [ ] **Intelligence Layer (Vollton):** Komplexe CI-Gates und breitere Diagnosen (`generate_supersession_map.py`, `generate_knowledge_gaps.py`) sind aktiv.
- [ ] **Reaktiver Loop:** Ein erster emergenter Kreislauf (STATE → SIGNAL → POLICY → ACTION → EVALUATION) ist als Testimplementierung aktiv.
- [ ] **Trigger-Mechanismen:** Die reaktiven Trigger (GitHub Actions vs. lokale Hooks) sind präzisiert.
- [ ] **Staleness/Retention-Strategie:** Archivierungsregeln (`experiments/_archive/`) halten die aktive Fläche klein.
- [ ] **AI-Onboarding & Viability Check:** Optionaler MCP-Bot für Onboarding ist evaluiert; quartalsweiser "Scope zurückbauen"-Check ist etabliert.

**Akzeptanzkriterien für Phase D (Optionale Schicht implementiert, wenn):**
- [ ] Mindestens ein reaktiver End-to-End-Loop (z.B. Auto-Ticket bei Staleness) läuft.
- [ ] Diagnosen wie Knowledge-Gaps oder Supersession-Maps werden generiert.
- [ ] Playbooks regeln den Umgang mit Tickets und Promotion-Anträgen.

## Die Intelligence Layer (Systemintelligenz)
Zusätzlich zur operativen Pipeline erhält das Repository eine leichte, maschinenlesbare Diagnostik- und Steuerungsebene.

**Operationalisierung der Intelligence Layer:**
- [ ] **Maschinenlesbare Repo-Verfassung:** `repo.meta.yaml` ist angelegt und definiert `canonical_sources`, `safe_read_paths` und `truth_model`.
- [ ] **Agentenführung:** `AGENTS.md` und `agent-policy.yaml` regeln den Umgang mit generierten Dateien und erzwingen Abbruch bei Konflikten.
    - [ ] *Lesereihenfolge für Agenten explizit gemacht:* `repo.meta.yaml` → `AGENTS.md` → `agent-policy.yaml` → `README.md` → `docs/index.md` → Kanonische Pfade → `docs/_generated/*`.
- [ ] **Dokumente als epistemische Objekte:** Ein `docmeta.schema.json` existiert in `contracts/`. Markdown-Dateien besitzen Pflicht-Frontmatter (`status`, `canonicality`, `relations`).
- [ ] **Diagnostische Generatoren:** `docs/_generated/` ist etabliert. *Regel: Diese Dateien sind reine Diagnose und werden niemals manuell editiert.*
- [ ] **Epistemische Dokumentpfade:** Der `docs/`-Ordner ist semantisch strukturiert (`concepts/`, `experiments/`, `syntheses/` etc.).
- [ ] **Minimaler Guard-/Generator-Stack:** Ein Lean-Startset liegt unter `scripts/docmeta/` (`validate_schema.py`, `validate_relations.py`, `generate_doc_index.py`, `generate_backlinks.py`, `generate_orphans.py`, `generate_system_map.py`).

## Kanonische Artefakte und Workflow
Die Pipeline stützt sich auf harte, schemavalidierte Artefaktarten vom Intake bis zum Export.

**Operationalisierung der Workflow-Pipeline:**
- [ ] **Hypothese (Intake):** Das YAML Issue-Formular `idea.yml` ist aktiv.
- [ ] **Experiment-Durchführung:** Ein Ordner wird basierend auf dem Golden Skeleton (`manifest.yml`, `method.md`, `evidence.jsonl`, `decision.yml`) befüllt.
- [ ] **Decision Artifact:** Meta-Entscheidungen (Metriken, Gate-Regeln) liegen typisiert unter `decisions/` (z.B. `process/`, `policy/`).
- [ ] **Katalogisierung (Promotion-PR):** Der PR prüft hart auf Existenz eines vollständigen Experiments (inkl. `CONTEXT.md` / `INITIAL.md` und `evidence.jsonl`), valide Schemas und synchronisierte Exports.
- [ ] **Benchmarks:** Definitionen liegen unter `benchmarks/criteria.md` und `challenges/`. Ergebnisse tragen eine `challenge_version`.
- [ ] **Instruction Block IR + Exports:** Die IR (`instruction-blocks/`) ist die alleinige Quelle; Änderungen erzwingen CI-Synchronisation der Ziel-Artefakte (`exports/`).
- [ ] **Regel für generierte Artefakte:** Generierte Artefakte (`exports/`, `.cursor/rules/`, `docs/_generated/`) werden **niemals manuell editiert**. *(Klarstellung: `repo.meta.yaml`, `AGENTS.md` und `agent-policy.yaml` sind handgepflegte Steuerungsdokumente).*

## Governance, Zonenmodell und Contribution Contract
Sicherheit und Qualitätsschranken sind architektonisch in zwei strikte Zonen unterteilt (Labor = freies Explorieren, Bibliothek = harte Validierung).

**Operationalisierung der Governance:**
- [ ] **Contribution Contract:** Jeder Beitrag ist zwingend typisiert (`Innovation`, `Experiment`, `Catalog Entry`, `Combo`, `Prompt`, `Decision Artifact`).
- [ ] **Traceability:** Jede reaktiv ausgelöste Aktion loggt `triggered_by`, `policy`, `action` und `outcome`.
- [ ] **Agenten- und Tool-Security:** Lokale Agenten und Cloud-Agenten sind in Experimenten explizit zu trennen.
- [ ] **Secret-/Konfigurationsverwaltung:** `.env.example` und `.gitignore` sind gepflegt; Push Protection und Secret Scanning sind aktiv.
- [ ] **Privacy-/Ethik-Policy:** Personenbezogene Daten und Secrets sind in `evidence.jsonl` und Artefakten untersagt (kodifiziert in `docs/policies/privacy-and-ethics.md`).
- [ ] **Prompt-Injection-Härtung:** Ein striktes Sanitization-Prinzip greift für Exporte.

---

## Einführungsreihenfolge (Der Baupfad)
*Dieser Pfad definiert, in welcher Reihenfolge die Repository-Struktur physisch aufgebaut werden soll, um den MVP erfolgreich bereitzustellen.*

- [ ] **Schritt 1: Operatives Fundament legen (MVP-Start)**
    - [ ] `README.md`, `CONTRIBUTING.md` und `.env.example` im Root anlegen.
    - [ ] `.github/CODEOWNERS` und `.github/ISSUE_TEMPLATE/` (idea, experiment-proposal, promotion-request) konfigurieren.
- [ ] **Schritt 2: Die Steuerungsdokumente (Intelligence Layer Basis)**
    - [ ] `repo.meta.yaml`, `AGENTS.md` und `agent-policy.yaml` verfassen.
    - [ ] `.vibe/` (intent, constraints, quality-gates) als Basis-Vertrag einrichten.
- [ ] **Schritt 3: Das Datenmodell (Schemas)**
    - [ ] `schemas/` für operative Validierung (Experiment, Catalog, Combo) anlegen.
    - [ ] `contracts/docmeta.schema.json` für die Dokumentsemantik anlegen.
- [ ] **Schritt 4: Die Labor-Umgebung**
    - [ ] `experiments/_template/` inklusive Golden Skeleton (`CONTEXT.md`, `INITIAL.md`, `manifest.yml`, `method.md`, `evidence.jsonl`, `decision.yml`) aufbauen.
- [ ] **Schritt 5: Die Bibliothek & Erkenntniswege (Stubs)**
    - [ ] `catalog/` (inkl. Unterordner `styles`, `workflows`, `anti-patterns`, `combos`), `prompts/adopted/` und `benchmarks/` anlegen.
    - [ ] `docs/` mit `index.md`, `masterplan.md` und den Basis-Strukturordnern (`_generated/` etc.) anlegen.
- [ ] **Schritt 6: Guard-Frontdoor & CI**
    - [ ] `Makefile` oder `.github/workflows/docs-guard.yml` einrichten.
    - [ ] `scripts/docmeta/` mit den Validatoren (`validate_schema.py`, `validate_relations.py`) und den Basis-Generatoren (`generate_doc_index.py`, `generate_backlinks.py`, `generate_orphans.py`, `generate_system_map.py`) bereitstellen.
- [ ] **Schritt 7: Erstbefüllung (Phase B)**
    - [ ] Golden Example in `experiments/` ausführen.
    - [ ] Erste Einträge in Katalog und Anti-Patterns überführen.

*Alles Weitere (Phase C/D: IR-Generatoren, Metrik-Dashboards, Knowledge-Gaps, Reaktiver Loop) wird erst hinzugefügt, wenn Schritt 1-7 stabil operieren.*

---

## Vorgeschlagene Zielstruktur
*Die Struktur zeigt das Zielbild, wird aber inkrementell besiedelt.*

```text
vibe-lab/
  Makefile                  # Schlanke Routine-Frontdoor (z.B. make validate, make vibe)
  README.md
  CONTRIBUTING.md           # Operatives Einstiegssystem
  .env.example              # Beispiel für erlaubte lokale Konfiguration
  docs/
    foundations/
      vision.md
      repo-plan.md
  repo.meta.yaml            # Maschinenlesbare Repo-Verfassung
  agent-policy.yaml         # Agentensteuerung
  AGENTS.md                 # Bindende Leseregeln für Agenten

  .github/
    ISSUE_TEMPLATE/
      idea.yml            # Typed Intake (Innovation)
      experiment-proposal.yml # Typed Intake (Experiment)
      promotion-request.yml   # Typed Intake (Catalog/Combo/Prompt)
    PULL_REQUEST_TEMPLATE/
      # [DEPRECATED] experiment-run.md removed in favor of default template
      promotion.md        # Das harte Gate
    workflows/
      validate.yml        # CI Schema-Prüfung
      docs-guard.yml      # Schlanke Guard-Frontdoor (Routine-Checks)
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
      CONTEXT.md          # Kontext-Engineering (Pflicht für Adopt-Kandidaten)
      INITIAL.md
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
    copilot/              # Info: Exporte enthalten Herkunftsmetadaten (generated_from, Hash, Timestamp)
    cursor/

  schemas/                # Bibliothek: Datenmodelle für CI-Checks (Pipeline-Validierung)
    experiment.manifest.schema.json
    catalog.entry.schema.json
    combo.schema.json

  docs/                   # Epistemische Dokumentpfade
    index.md              # Ausschließlich Navigation (keine Wahrheit)
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
    _generated/           # Diagnose-Artefakte (Ausschließlich Diagnose, nicht manuell editieren)
      doc-index.md
      backlinks.md
      orphans.md
      system-map.md
      metrics/            # Leichtgewichtiges Metrik-Dashboard
      stale-entries.md    # Phase C Generator-Output
      weak-links.md       # Phase C/D Generator-Output
      knowledge-gaps.md   # Phase C/D Generator-Output
      supersession-map.md # Phase C/D Generator-Output

  scripts/                # Minimaler Guard-/Generator-Stack (Frühschicht)
    docmeta/
      validate_schema.py
      validate_relations.py
      generate_doc_index.py
      generate_backlinks.py
      generate_orphans.py
      generate_system_map.py
      generate_stale_entries.py # Phase C/D Erweiterung
      generate_weak_links.py    # Phase C/D Erweiterung
      generate_knowledge_gaps.py # Phase C/D Erweiterung
      generate_supersession_map.py # Phase C/D Erweiterung

  tools/                  # CLI / Automatisierung
    vibe-cli/             # Scaffolding-CLI (spezifische Kommandos)
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
- **Dokumentsemantik und Diagnostik:** Markdown-Dateien als epistemische Objekte mit Frontmatter/Relations-Schema (`contracts/docmeta.schema.json`) definiert; `docs/_generated/` für Diagnoseartefakte und Guard-Scripts (`scripts/docmeta/`) integriert. Kanon, Navigation und Diagnose als strikt getrennte Wahrheitslogiken verankert.
- **Governance erweitert:** *Contribution Contract* eingefügt, der Beiträge zwingend in PR-Typen klassifiziert (Innovation, Experiment, Catalog Entry, Combo, Prompt, Decision Artifact) und jeweils eigene Qualitätsanforderungen auferlegt.
- **Kohärenz-Fixes:** Schema-Starter-Set exakt mit der `schemas/`-Ordnerstruktur synchronisiert (inkl. `combo.schema.json`) und Unterscheidung zwischen `contracts/` und `schemas/` klargestellt. `CONTRIBUTING.md` als operatives System dokumentiert. `blocked` als einziger operativer Pausenstatus normiert. Letzte Sichtbarkeitslücken (wie `CONTEXT.md` in der Templates-Struktur, `knowledge-gaps.md` im Baum und Export-Herkunftsmetadaten) geschlossen sowie `challenge_version`-Flexibilität und MVP-Scope im Text präzisiert. Harmonisierung der Generator-Skripte (`generate_knowledge_gaps.py`, `generate_supersession_map.py`) für Phase C/D und Aufnahme der `.env.example` in die Zielstruktur vollendet. Statuslogik (operativ vs. epistemisch) entwirrt und Promotion-Gate-Abfragen sprachlich differenziert. Sichtbarkeit des minimalen Früh-Stacks an Guard-Skripten im Baum geschärft und klare Agenten-Lesereihenfolge definiert. *Make-Frontdoor-Kohärenz hergestellt: `Makefile` als schlanke Routine-Frontdoor sichtbar verankert.* *AGENTS.md Kohärenz hergestellt: Aus der Liste der generierten Artefakte entfernt und explizit (gemeinsam mit `repo.meta.yaml` und `agent-policy.yaml`) als handgepflegtes, kanonisches Steuerungsdokument klassifiziert. Phasenmodell-Beschreibung sprachlich entdoppelt (Phase B ist die Erstbefüllung). Intake-Pfad für Decision Artifacts im Contribution Contract geklärt. Phase-A-Checkliste, Baupfad und Akzeptanzkriterien exakt auf die MVP-Pflichtelemente (docs/index.md, masterplan.md, volle Basis-Generatoren und Validatoren) synchronisiert.*
