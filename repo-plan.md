# Repository-Plan für vibe-lab

## Zielbild und Kernfähigkeiten
Das Repository soll ein exekutierbarer Erkenntnisraum sein: Es erfasst Vibe‑Coding‑Hypothesen, macht sie experimentierbar, zwingt zu Entscheidungen, konserviert Lerngewinne und liefert daraus praktische, wiederverwendbare Artefakte (Rules, Instructions, Prompt‑Bausteine, Workflows). Die Vision „Sammlung → Erprobung → Validierung → Kreation“ wird als Pipeline mit Rückkopplung umgesetzt: nichts bleibt „nur Idee“, aber auch nichts wird vorschnell als „Best Practice“ behauptet.

Daraus folgen Funktionen, die das Repo „können“ muss:

Erstens braucht es eine niedrigschwellige Intake‑Strecke (`innovations/inbox`): Ideen erfassen, ohne sofort zu überregulieren, aber mit minimaler Struktur, damit sie später experimentierbar sind. Für diese Art strukturierte Eingabe eignen sich Issue Forms in GitHub, weil sie YAML‑basierte Formulare mit Pflichtfeldern unterstützen und in `.github/ISSUE_TEMPLATE/` liegen.

Zweitens braucht es eine Experiment‑Engine, in der jede Hypothese als Experiment mit Manifest, Methode, Evidenz und Entscheidung abgelegt wird, und die sich per CI validieren lässt. Die Engine muss so gestaltet sein, dass sie “tribales Wissen” in reproduzierbare Artefakte übersetzt (oder sauber verwirft).

Drittens braucht es eine Bibliothek / Wissensdatenbank, die aus Experimenten nur das herauszieht, was den Gate bestanden hat: katalogisierte Practices (inkl. Anti‑Patterns), Kombinationsrezepte („combos“) und Benchmarks. Damit das nicht in einem Wiki endet, muss jedes Wissensartefakt auf Experimente verlinken und einen klaren Status tragen.

Viertens muss das Repo tool‑fähig sein: Es soll nicht nur Text sammeln, sondern Instruktions‑Artefakte erzeugen, die Agenten/Tools direkt lesen (z. B. Repo‑Instructions für GitHub Copilot und Rules für Cursor). Anforderungen und Speicherorte dafür sind tool-spezifisch (z. B. `.github/copilot-instructions.md` für repository-wide Instructions).

Fünftens muss das Repo Sicherheit und Governance als Produktfeature besitzen: klare Grenzen zwischen „Labor“ (frei, schnell, kurzlebig) und „Bibliothek“ (reviewpflichtig, validiert, stabil), inklusive Gates via Reviews, CODEOWNERS, Status Checks und Security Scans. CODEOWNERS ist dafür die Baseline, weil es Review‑Zuständigkeiten pfadbasiert definiert.

## Kanonische Artefakte und Datenmodelle
Damit die Pipeline wirklich funktioniert, braucht ihr wenige, aber harte kanonische Artefakte, die überall gleich aussehen. Der wichtigste Designhebel aus euren Plänen ist: nicht Prompts sammeln, sondern eine Zwischenrepräsentation (IR) für Agent‑Instruktionen pflegen und daraus Ziel‑Artefakte exportieren.

### Artefakt-Typen
Ein „perfektes“ vibe‑lab dreht sich um sieben Artefaktarten:

*   **Hypothese (Innovation)**: Ein einzelner, strukturierter Eintrag: Problem/Hypothese, Erfolgskriterium, Scope, Risiko, Kill‑Kriterium, nächste Aktion. Das ist die Einheit, die in die Pipeline geht.
*   **Experiment**: Ein Ordner, der mindestens Manifest, Methode, Resultat, Entscheidung und Evidenz enthält (plus erzeugte Artefakte). Damit wird aus „ausprobieren“ ein überprüfbarer Prozess.
*   **Decision Artifact (Meta-Entscheidung)**: Entscheidungen über das System selbst: Metriken, Gate‑Regeln, Export‑Targets, De‑/Re‑Katalogisierung. Diese Entscheidungen sind nicht „Nebenbei‑Notizen“, sondern steuern die Evolution.
*   **Catalog Entry (Practice / Anti‑Pattern)**: Ein kuratierter Eintrag mit Status und Evidenzlevel, der auf Experimente verweist. Der Katalog ist das stabile Interface nach außen.
*   **Combo**: Eine getestete Kombination aus mindestens zwei Achsen (z. B. Stil + Tool, Technik + Workflow) mit expliziten Synergien/Anti‑Synergien.
*   **Benchmarks**: Definition harter Kernmetriken (Time‑to‑Running, Rework‑Zyklen, Acceptance Rate, Manual Intervention) und strukturierte Ergebnisse.
*   **Instruction Block IR + Exports**: Engine‑neutraler Block, aus dem tool‑spezifische Instructions (Copilot), Rules (Cursor), AGENTS‑Hinweise etc. generiert werden.

### Minimal-Schemata (Formatvorschlag)
Damit CI automatisiert validieren kann, stehen alle kanonischen Dateien unter `schemas/` als JSON Schema / YAML Schema und werden in “Library‑Zonen” strikt durchgesetzt. (Im Labor ist die Validierung lockerer, damit der Flow nicht stirbt.)

**Experiment Manifest (manifest.yml) – Vorschlag:**
```yaml
id: 2026-04-08_spec-first-vs-yolo
title: "Spec-First vs YOLO: Mehrrepo-Refactor"
hypothesis: "Spec-First reduziert Rework-Zyklen bei gleicher Time-to-Running"
setup:
  tools: [cursor, copilot]
  style: spec-first
  repo_scope: "multi-repo"
metrics:
  primary: [time_to_running, rework_cycles, acceptance_rate, manual_intervention]
  secondary: [flow_rating, friction_notes]
inputs:
  contracts: [.vibe/constraints.yml, .vibe/quality-gates.yml]
outputs:
  export_targets: [cursor_rules, copilot_repo_instructions, agents_md]
```

**Experiment Decision (results/decision.yml) – Vorschlag:**
```yaml
decision: adopt # adopt | reject | iterate
confidence: medium # low | medium | high
evidence_level: compared # none | anecdotal | compared | benchmarked
reproducibility: medium # low | medium | high
rationale:
  - "rework_cycles reduced"
  - "quality_gates passed"
followups:
  - "extract instruction block for spec-first workflow"
```

**Catalog Entry Frontmatter – Vorschlag (kompatibel zur Status‑Logik in euren Plänen):**
```yaml
---
name: "Spec-First Vibe"
category: workflow
status: adopted # idea | testing | adopted | rejected | deprecated
evidence_level: compared
tools: [cursor, copilot]
synergies: [tdd-vibe]
anti_synergies: [yolo-prompting]
linked_experiments: ["2026-04-08_spec-first-vs-yolo"]
last_tested: 2026-04-08
---
```
Der zentrale Vorteil dieser Strenge ist nicht „Ordnung“, sondern dass ihr daraus automatisch Indizes, Übersichten und Release Notes generieren könnt, ohne zu fluten.

## Workflow: Von Idee zu Practice und zurück
Der „perfekte“ Ablauf ist eine Pipeline mit klaren Zustandswechseln, die in PRs sichtbar wird und möglichst viel automatisch überprüft.

### Intake und Triage
Die schnellste Einlassschleuse ist ein Issue Form „Idea / Hypothesis“, das direkt Metadaten erfasst (Hypothese, Erfolgskriterium, Stack/Tool, Risiko). Issue Forms sind YAML‑basiert und liegen in `.github/ISSUE_TEMPLATE/`.

In der Praxis bekommt jede Hypothese einen eindeutigen slug/id und wird entweder:
1.  in `innovations/` als Datei materialisiert (wenn ihr file-first arbeiten wollt), oder
2.  als Issue geführt, das später im Experiment‑Ordner referenziert wird (wenn ihr issue-first arbeitet).

Beides funktioniert; entscheidend ist, dass Promotion nur über einen PR passiert.

### Experimente als First-Class-Objekte
Jedes Experiment lebt in `experiments/YYYY-MM-DD_slug/` und enthält mindestens diese Bausteine:
*   `manifest.yml` (Ziel, Hypothese, Setup, Metriken)
*   `method.md` (Ablauf, Variablen, Eingriffe)
*   `results/result.md` (Ergebnisdarstellung)
*   `results/decision.yml` (adopt | reject | iterate)
*   `results/evidence.jsonl` (Rohereignisse)
*   `artifacts/` (Rules, Prompts, Diffs, Outputs)

Das Repo kann das als „golden skeleton“ per Generator unter `tools/` bereitstellen, damit die Einstiegshürde gering bleibt.

### Promotion und Katalogisierung
Promotion ist eine zweite PR‑Art, die ausschließlich den Katalog/Libraries betrifft. GitHub unterstützt mehrere PR‑Templates, wenn ihr sie unter `.github/PULL_REQUEST_TEMPLATE/` als mehrere Dateien ablegt; je nach Workflow kann man Templates per Parameter auswählen.

Promotion‑PR prüft:
*   existiert ein Experiment‑Ordner mit vollständigem Manifest/Decision/Evidence?
*   sind die Schemas valide?
*   ist der Catalog‑Eintrag korrekt verlinkt?
*   wurden Export‑Artefakte aktualisiert (falls aus IR generiert)?
*   laufen Quality Gates (Guardrails) durch?

### Rückkopplung und Revision
Die Pipeline ist absichtlich nicht linear. Drei Feedback-Routen müssen explizit vorgesehen sein:
1.  Adopted Practices → neue Experimente (Stabilisierung und Vergleich)
2.  Lab/Innovation → neue Experimente (Exploration)
3.  Experimente → Revision bestehender Practices (Deprecation / Update)

Damit das „sichtbar“ bleibt, sollte jede Practice ein Re‑Test‑Feld (`last_tested`) besitzen und die CI in regelmäßigen Abständen „stale“ Einträge markieren (z. B. per Issue).

## Governance, Sicherheit und Qualitätsschranken
Der Plan aus euren Texten ist richtig: zwei Qualitätszonen (Labor/Bibliothek) und dazwischen ein Gate. Der perfekte Repo‑Plan macht daraus konkrete, überprüfbare Regeln.

### Ownership und Review-Pflichten
CODEOWNERS ist das Kernstück: Es weist Pfade Ownern zu, sodass Reviews automatisch an die richtigen Personen/Teams gehen.

Ergänzend setzt ihr Branch Protection oder Rulesets ein, um Reviews und Checks zwingend zu machen. GitHub Protected Branches können Required Status Checks und Review‑Anforderungen erzwingen.

Wenn ihr feiner steuern wollt (z. B. unterschiedliche Regeln für `catalog/` vs `innovations/`), sind Repository Rulesets eine passende Erweiterung.

### Security, Supply Chain und „Vibe ohne Rootzugriff“
Für ein Repo, das Experimente und Tooling akkumuliert, sind vier Sicherheits-Layer sinnvoll:
1.  Dependabot für Dependency Updates (supply-chain Hygiene).
2.  CodeQL Code Scanning (wenn ihr Code im Repo habt; bei reinen Markdown-Repos weniger relevant).
3.  Secret Scanning / Push Protection (um Leaks früh zu blocken).
4.  OpenSSF Scorecard (als Meta‑Signal für Security Best Practices, besonders bei public repo).

Für Binär‑Assets (z. B. UI‑Exports, Videos) ist Git LFS die robuste Option, weil Git sonst historisch „aufbläht“; Git LFS speichert Pointer im Repo und lagert große Inhalte aus.

## Dokumentation als lebendes Interface
Eure Pläne setzen auf Mermaid‑Diagramme, weil sie in GitHub‑Markdown direkt gerendert werden, wenn sie in einem `mermaid`‑Codeblock stehen.

Für eine durchsuchbare Docs‑Site ist Material for MkDocs eine naheliegende Wahl, weil es client‑seitige Suche „out of the box“ liefert.

Wenn ihr Design Tokens/Design‑System‑Artefakte wirklich integriert, sollte das Tokenformat DTCG-konform sein, weil es als Austauschformat gedacht ist.

## Automatisierung und Tool-Integration
Die Umsetzungsidee ist: ein kanonischer Kern, mehrere Export‑Targets. Das verhindert „Prompt Zoo“, weil ihr nicht pro Tool unterschiedliche Wahrheiten pflegt.

### Tool-spezifische Instructions als Export-Ziele
*   Für GitHub Copilot sind repo‑weite Instructions als `.github/copilot-instructions.md` dokumentiert.
*   Für Cursor sind projektnahe Rules in `.cursor/rules/` (und ergänzend `AGENTS.md`) in deren Doku vorgesehen.

Der perfekte Plan macht die IR (Instruction Blocks) kanonisch und generiert daraus:
*   `.github/copilot-instructions.md` (oder Teile davon)
*   `.cursor/rules/*.mdc`
*   `AGENTS.md`
*   eventuell `.vibe/` Defaults (Constraints/Gates)

Wichtig ist hier nicht der Generator an sich, sondern dass CI prüft: Exports sind synchron. Das kann über „generated files must match“ geschehen (Diff fails).

### CI/Checks, die wirklich zählen
Ihr braucht wenige Checks, die den Pipelinecharakter tragen:
*   **Schema Validierung:** Catalog Entries, Experiments, Decisions, Instruction Blocks.
*   **Link Integrity:** „Catalog → Experiments“ muss existieren.
*   **Promotion Gate:** Änderungen in `catalog/` dürfen nur per Promotion‑PR passieren (Review + Checks).
*   **Docs Build:** Indizes und Übersichten werden automatisch aus Frontmatter gebaut.
*   **Security** (optional je nach Code-Anteil): Dependabot, CodeQL, Push Protection, Scorecard.

## Vorgeschlagene Repostruktur
Die Struktur unten ist eine Synthese der besten Elemente aus euren Plänen: Lab vs Library (Plan1/Vision), Exploration→Selektion→Promotion→Observability (Plan2), `.vibe/` Contracts + Pipeline + Guardrails (Plan3), Catalog/Experiments/Benchmarks + Statusmodell (Plan4).

Sie ist so gebaut, dass ihr sie in drei Ausbaustufen nutzen könnt:
1.  nur `innovations/` + `experiments/` (MVP)
2.  plus `catalog/` + `schemas/` + `tools/` (System wird sichtbar)
3.  plus `exports/` + `docs/` (Tool-Readiness & Distribution)

```text
vibe-lab/
  README.md
  vision.md
  CONTRIBUTING.md
  LICENSE
  SECURITY.md
  CODE_OF_CONDUCT.md

  .github/
    ISSUE_TEMPLATE/
      idea.yml
      experiment.yml
      promotion.yml
    PULL_REQUEST_TEMPLATE/
      lab-spike.md
      experiment-run.md
      promotion-to-catalog.md
    workflows/
      validate-schemas.yml
      build-docs.yml
      security-codeql.yml
      security-scorecard.yml
    dependabot.yml
    CODEOWNERS
    copilot-instructions.md

  .vibe/
    intent.md
    constraints.yml
    quality-gates.yml
    contracts.schema.json

  .cursor/
    rules/
      README.md
      style.mdc
      safety.mdc

  AGENTS.md

  innovations/
    README.md
    2026-04-08_spec-first-vs-yolo.md

  experiments/
    _template/
      manifest.yml
      method.md
      results/
        decision.yml
        result.md
        evidence.jsonl
      artifacts/
    2026-04-08_spec-first-vs-yolo/
      manifest.yml
      method.md
      results/
        decision.yml
        result.md
        evidence.jsonl
      artifacts/
        diffs/
        rules/
        prompts/
        instructions/

  catalog/
    styles/
    technologies/
    techniques/
    workflows/
    anti-patterns/
    combos/

  combos/
    README.md
    spec-first__cursor.md

  benchmarks/
    criteria.md
    results/

  instruction-blocks/
    _schema/
    spec-first-vibe.yml

  exports/
    copilot/
      copilot-instructions.generated.md
    cursor/
      rules.generated/
    agents/
      AGENTS.generated.md

  schemas/
    experiment.manifest.schema.json
    experiment.decision.schema.json
    catalog.entry.schema.json
    instruction-block.schema.json
    benchmark.result.schema.json

  docs/
    index.md
    playbooks/
      triage.md
      promotion.md
      security.md
    onboarding/
      first-30-min.md

  tools/
    create-experiment/
    validate/
    export/
    build-docs/
```

### Warum genau so?
Die Pipeline‑Ordner (`innovations/` → `experiments/` → `catalog/`) machen den Erkenntniskreislauf sichtbar und zwingen euch zu Beweglichkeit. Das Lab/Bibliothek‑Prinzip wird dadurch praktisch: Alles, was „frei“ sein darf, lebt in `innovations/` und `experiments/`; alles, was „stabil“ sein muss, lebt in `catalog/`, `benchmarks/` und `exports/` und ist streng validiert.

Die `.github/`‑Schicht bildet die Governance ab: Issue Forms und PR Templates standardisieren Eingaben, CODEOWNERS und Branch Protection / Rulesets machen die Übergänge verbindlich.

Die Tool‑Readiness entsteht durch klare, dokumentierte Speicherorte: Copilot liest repo‑weite Instructions über `.github/copilot-instructions.md`, Cursor über `.cursor/rules/` und ergänzende Agent‑Dateien.

Die Dokumentations- und Visualisierungsebene bleibt „leicht“: Mermaid‑Diagramme funktionieren direkt in GitHub‑Markdown, während eine optionale Docs‑Site über MkDocs Material durchsuchbar wird, wenn ihr sie braucht.
