---
title: "Blueprint — Agent/Skill Minimal Layer v0.1"
status: draft
canonicality: exploratory
created: "2026-05-01"
updated: "2026-05-01"
author: "agent"
relations:
  - type: derived_from
    target: "./blueprint-agent-operability.md"
  - type: derived_from
    target: "./blueprint-v2.md"
  - type: references
    target: "../../.github/agents/experiment-critic.agent.md"
  - type: references
    target: "../../.github/agents/experiment-operator.agent.md"
  - type: references
    target: "../concepts/execution-bound-epistemics.md"
  - type: references
    target: "../policies/interpretation-budget.md"
  - type: informs
    target: "../../.github/agents/experiment-critic.agent.md"
---

# Blueprint — Agent/Skill Minimal Layer v0.1

## Status dieser Datei

Diese Datei ist ein **explorativer Blueprint**.

- Sie **implementiert** den Agent/Skill Minimal Layer nicht.
- Sie erzeugt keine neue Enforcement-Autorität.
- Sie ist keine Policy, kein Schema, kein Validator und kein CI-Guard.
- Verbindliche Durchsetzung entsteht erst durch spätere Agent-Dateien,
  Scripts, Schemas oder CI-Checks.

Maßgebliche Wahrheitsquellen bleiben: `repo.meta.yaml`, `AGENTS.md`,
`agent-policy.yaml`, `contracts/`, `schemas/`, `.vibe/`.

---

## Ziel

Minimale Schicht zur Reduktion von vier beobachteten Fehlklassen:

1. **Task-Unschärfe** — Aufgaben ohne auflösbaren Locator oder eindeutigen `change_type`
2. **Scope Drift** — stille Erweiterung von `target_files` über den deklarierten Scope hinaus
3. **Unbelegte Erfolgsclaims** — `PASS`-Urteile ohne überprüfbaren Evidence-Trail
4. **Formale Gültigkeit ohne semantischen Nachweis** — strukturell valide Handoffs, die inhaltlich nicht prüfbar sind

**Nicht-Ziel:** Neue Rollen-, Skill- oder Prompt-Komplexität ohne belegbaren operativen Nutzen. Kein Aufbau konkurrierender Agenten-Dateien zum bestehenden Critic/Operator-Modell.

---

## Evidenzbasis

Diese Blaupause reagiert auf Fehlklassen, die im Repo explizit modelliert sind:

- `experiments/2026-04-15_agent-task-validity/` unterstützt die Arbeitshypothese,
  dass explizite `target_files`, Locator und `change_type` die Ausführbarkeit
  und Reviewbarkeit von Agentenaufgaben verbessern können. Die Evidenz bleibt
  begrenzt und benötigt Replikation.
- `docs/concepts/execution-bound-epistemics.md`: epistemologische Basis für
  Claim-Bindung an Evidence.
- `docs/policies/interpretation-budget.md`: Grenze für Interpretation ohne Beleg.
- Bestehende Critic/Operator-Handoffs: formale Struktur vorhanden, semantische
  Prüfung der Claims noch nicht systematisiert.

Diese Datei beweist nicht, dass die geplante Schicht nützlich ist.
Das Evaluation-Dokument (→ PR-1) übernimmt diese Aufgabe.

---

## Begriffliche Grenze

**Agent** bezeichnet hier eine rollenbasierte Arbeitsinstanz mit klarer
Zuständigkeit, Eingabegrenzen, Output-Format und expliziten Nicht-Zielen.
Der Begriff folgt dem bestehenden Sprachgebrauch in `.github/agents/`.

**Skill** bezeichnet hier ausschließlich ein wiederverwendbares
Instruktionsmuster. Kein neuer Repo-Artefakttyp. Keine neue Autorität.

**Blaupause** ist ein Planartefakt, kein Bauwerk. Diese Datei beschreibt
Intention, Scope und Falsifikationsgrenzen — keine fertige Implementierung.

---

## Leitentscheidung

Nicht mehr Agenten bauen. Bestehende Autorität verdichten.

```
bestehender experiment-critic
  → Non-Ideal Task Guard (Erweiterung, kein neuer Agent)

bestehender experiment-operator
  → unverändert; führt nach Critic-PASS aus

neuer evidence-reconciliation-auditor
  → Claim ↔ Evidence Reconciliation (neuer Agent)

neues Evaluation-Dokument
  → Nutzennachweis oder Falsifikation

später, nach realem Einsatz
  → Script-/CI-Enforcement statt reiner Agentendisziplin
```

---

## Folge-PR Scope: PR-1

Die folgenden Kriterien gelten für **PR-1**, nicht für diese Blueprint-Datei.

### Genau diese drei Änderungen

| # | Datei | Operation |
|---|-------|-----------|
| 1 | `.github/agents/experiment-critic.agent.md` | erweitern um Non-Ideal Task Guard |
| 2 | `.github/agents/evidence-reconciliation-auditor.agent.md` | neu anlegen |
| 3 | `docs/evaluations/agent-skill-file-fruitfulness.md` | neu anlegen |

### Explizit nicht ändern

- `scripts/`
- `schemas/`
- `.github/workflows/`
- `docs/_generated/` (nur generatorbasiert)
- `contracts/`
- `.vibe/`

---

## Geplanter Inhalt: Non-Ideal Task Guard

**Zieldatei:** `.github/agents/experiment-critic.agent.md` — neuer Abschnitt,
kein konkurrierender Agent.

**Zweck:** Verhindert, dass der Critic eine unklare Aufgabe durch Interpretation
auffüllt. Blockiert nicht-ausführbare Tasks härter als die heutige
Operability-Check-Logik.

**Entwurf:**

```markdown
## Non-Ideal Task Guard
This guard does not replace the existing Operability Criteria or A1–A3 checks.
It only defines conditions under which the Critic must not return `PASS`.
A task must not receive `PASS` if any of the following applies:
- the locator cannot be resolved from the currently read repository state
- validation cannot distinguish a real change from a no-op
- the task requires evidence that has not been read
- exact_before/exact_after is necessary to prevent ambiguity but absent
- multiple independent changes are silently combined
- target_files are formally present but too broad for a bounded edit
If any condition applies:
- return `PARTIAL` or `FAIL`
- never return `PASS`
- mark the first blocking condition explicitly with `MISSING`, `UNKNOWN`, or `BLOCKED_BY`
- prefer task split over scope expansion
```

Dieses Muster ist keine zweite Operability-Liste. Es ist eine No-PASS-Schranke:
Der Guard wird nur aktiv, wenn der Critic andernfalls `PASS` zurückgeben würde,
obwohl eine der genannten Blocking-Bedingungen erfüllt ist.

---

## Geplanter Inhalt: Evidence Reconciliation Auditor

**Zieldatei:** `.github/agents/evidence-reconciliation-auditor.agent.md`

**Zweck:** Nachlaufprüfung, ob behauptete Änderungen und
Validierungsergebnisse durch Repo-Evidence belegt sind.

**Kernprinzip:** Kein Claim ohne Evidence.

**Frontmatter-Entwurf:**

```yaml
name: evidence-reconciliation-auditor
description: "Prüft nach Operator-Ausführung, ob Claims durch Repo-Evidence belegt sind."
tools: [read, search]
model: "GPT-5 (copilot)"
user-invocable: true
```

**Feste Verdicts:**

| Verdict | Bedeutung |
|---------|-----------|
| `PASS` | Alle Claims belegt |
| `CLAIM_NOT_PROVEN` | Claim vorhanden, Evidence fehlt |
| `CONTRADICTION` | Claim widerspricht vorgefundener Evidence |
| `MISSING_EVIDENCE` | Evidence-Quelle nicht auffindbar |
| `OUT_OF_SCOPE` | Claim außerhalb deklariertem Scope |
| `NOT_REPRODUCIBLE` | Claim nicht nachstellbar aus Repo-State |

**Pflichtprüfung:**

| Claim-Typ | Erforderliche Evidence |
|-----------|------------------------|
| Datei geändert | Diff, exakter Dateiinhalt oder belegter Target-Read |
| Generated Artifact aktualisiert | Generator-Output, Diff oder begründeter No-Change |
| Command erfolgreich | exakter Command-Output |
| Validator erfolgreich | exakter Validator-Output |
| Decision aktualisiert | Konsistenz zwischen Decision, Result und Evidence |
| Scope eingehalten | tatsächliche Touched Files entsprechen Zielscope |

**Pflichtausgabe-Struktur:**

```markdown
## Verdict
...
## Proven Claims
...
## Unproven Claims
...
## Contradictions
...
## Missing Evidence
...
## Required Next Proof
...
```

**Grenze:** Der Auditor ist transitional. Endgültige Autorität soll in
Scripts, Schemas oder CI liegen. Er verlängert die bestehende
Critic/Operator-Kette um eine nachgelagerte Claim-Prüfstufe.

**Boundary:**

```markdown
## Boundary
This auditor does not judge whether the change was a good idea.
It only checks whether claims are supported by repository evidence.
The auditor must not:
- repair claims
- edit files
- infer missing evidence
- upgrade plausible claims into proven claims
- validate semantic usefulness beyond available evidence
```

---

## Geplanter Inhalt: Evaluation-Dokument

**Zieldatei:** `docs/evaluations/agent-skill-file-fruitfulness.md`

**Zweck:** Prüfen, ob Agent-/Skill-Dateien tatsächlich nützen oder nur
zusätzliche Instruktionsfläche erzeugen.

**Mindestinhalt:**

- Frage: Wann verbessern Agent-/Skill-Dateien die Repo-Arbeit?
- Hypothese + Non-Hypothese
- Evaluation Matrix
- Metriken (s.u.)
- Falsifikationskriterien (s.u.)
- Interpretation Budget

**Metriken:**

```
scope_drift_count
unsupported_claim_count
missing_locator_count
validation_gap_count
review_friction_count
rework_count
false_block_count
task_completion_time_delta
```

**Falsifikationskriterien** — die Schicht ist nicht nützlich, wenn über
mindestens drei vergleichbare PRs gilt:

- unbelegte Claims sinken nicht
- Scope Drift sinkt nicht
- Review Friction sinkt nicht
- False Blocks steigen stärker als Fehler sinken
- Task-Dauer steigt ohne erkennbare Qualitätsverbesserung
- spätere CI-/Script-Rückbindung bleibt aus

---

## Bewusst nicht gebaut

| Datei | Grund |
|-------|-------|
| `task-contract-critic.agent.md` | Redundant zum bestehenden `experiment-critic` |
| `claim-budget.md` | Gehört in Interpretation-Budget-Logik oder das Evaluation-Dokument |
| `locator-bound-change.md` | Als eigene Skill-Datei zu schmal; Locator-Bindung im Critic verankern |
| `diagnose-before-patch.md` | Bereits Teil des bestehenden Operator-Modells |

---

## Akzeptanzkriterien

### Für diese Blueprint-Datei

- [ ] Begrenzt ihre eigene Autorität klar
- [ ] Behauptet keine Umsetzung
- [ ] Trennt Folge-PR-Scope von Blueprint-Status
- [ ] Führt `Skill` nicht als neue Repo-Artefaktklasse ein
- [ ] Enthält Falsifikationsgrenzen
- [ ] Ändert keine Scripts, Schemas oder Workflows
- [ ] Ändert Generated Files nur generatorbasiert

### Für PR-1

- [ ] Scope strikt auf die drei PR-1-Dateien begrenzt
- [ ] Keine unerlaubten Nebenänderungen
- [ ] Non-Ideal Task Guard eindeutig und nicht-überlappend mit bestehenden A1–A3-Checks
- [ ] Auditor besitzt feste Verdicts und strukturierte Pflichtausgabe
- [ ] Evaluation-Dokument ist falsifizierbar, nicht dogmatisch
- [ ] `make generate-blocking` ausgeführt oder Fehlerausgabe exakt dokumentiert
- [ ] `make validate` ausgeführt oder Fehlerausgabe exakt dokumentiert

---

## Falsifikationsgrenze dieser Blaupause

Diese Blaupause ist zu verwerfen oder zu überarbeiten, wenn:

- die geplante Agent-Schicht unbelegte Claims nach drei vergleichbaren PRs nicht reduziert
- Scope Drift nicht sinkt
- False Blocks stärker steigen als Fehler sinken
- die Schicht ohne spätere Script-/CI-Rückbindung bleibt
- neue Begriffsdrift zwischen Agent, Skill, Policy und Contract entsteht
- diese Datei von Agenten als bereits implementierte Architektur fehlgelesen wird

---

## Risiko / Nutzen

**Nutzen:**
- Klare Autoritätsstruktur ohne neue konkurrierende Dateien
- Bessere Claim-Prüfung durch Auditor-Zwischenstufe
- Weniger Redundanz durch bewusste Nicht-Erweiterung
- Messbare Falsifikationsschwelle

**Risiko:**
- Anfängliche Scheinsicherheit ohne CI-Rückbindung
- Zusätzlicher Audit-Aufwand durch Auditor-Zwischenstufe
- Mögliche False Blocks bei zu strengem Non-Ideal Task Guard
- Blueprint altert, sobald PR-1 umgesetzt ist → Status dann auf
  `implemented`, `superseded` oder `archived` setzen

**Minderung:**
- `status: draft`, `canonicality: exploratory`
- Explizite Falsifikationskriterien
- Evaluation-Dokument als Nutzennachweis-Pflicht

---

## Geplante Checks nach PR-1

```bash
make generate-blocking
make validate
```

Regeln:
- Änderungen aus `make generate-blocking` mitführen
- Bei `make validate`-Fehlern exakten Output dokumentieren, nicht heuristisch reparieren
- Keine manuellen Änderungen an `docs/_generated/`

---

## Nächste Aktion

Separater PR-1 mit genau diesen drei Zielartefakten:

1. `.github/agents/experiment-critic.agent.md` — Non-Ideal Task Guard ergänzen
2. `.github/agents/evidence-reconciliation-auditor.agent.md` — neu anlegen
3. `docs/evaluations/agent-skill-file-fruitfulness.md` — neu anlegen

Dieser Blueprint bleibt bis dahin Planartefakt mit `status: draft`.
