---
title: "Agent/Skill File Fruitfulness"
status: draft
canonicality: evaluative
created: "2026-05-01"
updated: "2026-05-01"
relations:
  - type: derived_from
    target: "../blueprints/blueprint-agent-skill-minimal-layer-v0.1.md"
  - type: references
    target: "../../.github/agents/experiment-critic.agent.md"
  - type: references
    target: "../../.github/agents/evidence-reconciliation-auditor.agent.md"
  - type: references
    target: "../policies/interpretation-budget.md"
---

# Agent/Skill File Fruitfulness

## Status dieser Datei

Diese Datei ist ein **evaluatives Planartefakt**.

- Sie behauptet **nicht**, dass Agent-/Skill-Dateien bereits nützlich sind.
- Sie definiert ausschließlich, **wie** Nutzen künftig gestützt oder
  falsifiziert werden kann.
- Sie ersetzt keine bestehende Validator-, Schema- oder CI-Autorität.
- Sie erhebt keine eigenen Enforcement-Ansprüche.

Quelle: `docs/blueprints/blueprint-agent-skill-minimal-layer-v0.1.md`.

---

## Frage

Wann verbessern Agent-/Skill-Dateien die Repo-Arbeit, und wann erzeugen sie
nur zusätzliche Instruktionsfläche ohne erkennbaren Nutzen?

---

## Begriffliche Grenze: Agent file vs. Skill file

**Agent file** (`.github/agents/*.agent.md`):
Rollenbasierte Arbeitsinstanz mit klarer Zuständigkeit, Eingabegrenzen,
Output-Format und expliziten Nicht-Zielen. Bestehender Repo-Artefakttyp.

**Skill file**:
Wiederverwendbares Instruktionsmuster. Kein neuer Repo-Artefakttyp.
Keine neue Autorität. Skill-Dateien werden in dieser Evaluation nur als
Begriff geführt; ihre Repo-Anlage ist ausdrücklich kein Ergebnis dieser
Evaluation.

Diese Evaluation prüft beide Begriffe getrennt. Agent-Dateien werden anhand
realer PR-Daten gemessen; Skill-Dateien bleiben so lange unbeurteilt, wie
keine Repo-Realisierung existiert.

---

## Hypothese

Agent-/Skill-Dateien sind dann fruchtbar, wenn sie über mindestens drei
vergleichbare PRs hinweg messbar:

- unbelegte Erfolgsclaims reduzieren
- Scope Drift reduzieren
- Review Friction reduzieren
- ohne dabei False Blocks stärker steigen zu lassen als Fehler sinken

Fruchtbarkeit ist hier nicht ästhetisch, sondern funktional definiert:
weniger Korrekturzyklen, weniger unbelegte Behauptungen, klarer abgrenzbare
Reviewbarkeit.

---

## Non-Hypothese

Diese Evaluation behauptet **nicht**:

- dass Agent-Dateien grundsätzlich nützlich sind
- dass mehr Agent-Dateien zu besseren Ergebnissen führen
- dass Skill-Dateien als Repo-Artefakt eingeführt werden sollten
- dass diese normative Schicht eine spätere Script-/CI-Rückbindung ersetzen kann
- dass formal saubere Handoffs gleichbedeutend mit semantisch geprüfter Qualität sind

Eine bestätigte Hypothese in dieser Evaluation ist eine notwendige, keine
hinreichende Bedingung für eine spätere Verstetigung.

---

## Evaluation Matrix

| Beobachtung | Agent-/Skill-Schicht hilft | Agent-/Skill-Schicht ist neutral | Agent-/Skill-Schicht schadet |
|---|---|---|---|
| Unbelegte Claims pro PR | sinkt | unverändert | steigt |
| Scope Drift pro PR | sinkt | unverändert | steigt |
| Fehlende Locator pro Task | sinkt | unverändert | steigt |
| Validation Gaps pro PR | sinkt | unverändert | steigt |
| Review Friction (Reviewer-Zyklen) | sinkt | unverändert | steigt |
| Rework pro PR | sinkt | unverändert | steigt |
| False Blocks (Critic blockt valide Tasks) | konstant oder ↓ | leicht ↑, aber < Fehlerreduktion | ↑ stärker als Fehlerreduktion |
| Task-Dauer | konstant oder ↓ | ↑ mit erkennbarer Qualitätsverbesserung | ↑ ohne Qualitätsverbesserung |

Eine Spalte allein entscheidet nicht. Bewertung erfolgt nur über die
Gesamtmatrix und nur über mindestens drei vergleichbare PRs.

---

## Metriken

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

Definitionen:

- `scope_drift_count` — Touched Files außerhalb des deklarierten Scopes pro PR
- `unsupported_claim_count` — vom Auditor als `CLAIM_NOT_PROVEN`, `MISSING_EVIDENCE`, `CONTRADICTION` oder `NOT_REPRODUCIBLE` markierte Claims pro PR
- `missing_locator_count` — Critic-Tasks mit `MISSING`/`UNKNOWN`/`BLOCKED_BY` für Locator
- `validation_gap_count` — Claims „validator succeeded" ohne exakten Validator-Output
- `review_friction_count` — Reviewer-Runden vor Merge
- `rework_count` — Folge-Commits, die frühere Aussagen desselben PRs revidieren
- `false_block_count` — Critic-`FAIL`/`PARTIAL` für Tasks, die später unverändert ausführbar werden
- `task_completion_time_delta` — Differenz zwischen Task-Dauer mit und ohne diese Schicht über vergleichbare PRs

Erhebung erfolgt manuell aus PR- und Agent-Output. Diese Evaluation legt
keine automatisierte Messpipeline an.

---

## Falsifikationskriterien

Die Schicht gilt als **nicht nützlich oder überarbeitungsbedürftig**, wenn
über mindestens drei vergleichbare PRs gilt:

- unbelegte Claims sinken nicht
- Scope Drift sinkt nicht
- Review Friction sinkt nicht
- False Blocks steigen stärker als Fehler sinken
- Task-Dauer steigt ohne erkennbare Qualitätsverbesserung
- spätere Script-/CI-Rückbindung bleibt aus

Trifft mindestens eines dieser Kriterien zu, muss der Blueprint
`docs/blueprints/blueprint-agent-skill-minimal-layer-v0.1.md` revidiert,
zurückgenommen oder als `superseded` markiert werden.

---

## Interpretation Budget

- Beobachtet werden ausschließlich PRs, in denen sowohl `experiment-critic`
  als auch `evidence-reconciliation-auditor` tatsächlich aktiv eingesetzt
  wurden. Nicht-Nutzung ist kein Beleg für Nutzlosigkeit, sondern fehlende
  Datengrundlage.
- Drei vergleichbare PRs sind die Mindestmenge für ein Verdict.
  Einzelne PRs erlauben keine Aussage über Fruchtbarkeit.
- „Vergleichbar" heißt: ähnlicher Scope, ähnliche Repo-Zone, ähnlicher
  Änderungstyp. Cross-Zone-Vergleiche sind unzulässig.
- Aus reduzierten Metriken folgt nicht, dass die Reduktion durch die
  Agent-Schicht verursacht wurde. Kausalität bleibt unbelegt, solange kein
  Vergleich gegen vergleichbare PRs ohne diese Schicht vorliegt.
- Aus erfüllten Falsifikationskriterien folgt, dass die Schicht in ihrer
  aktuellen Form nicht trägt. Es folgt nicht, dass das gesamte Konzept
  unbrauchbar ist.
- Diese Evaluation darf nicht als Beweis für die Wirksamkeit der Schicht
  zitiert werden, solange weniger als drei vergleichbare PRs vorliegen.

---

## Nächste Datenerhebung

1. Erste vergleichbare PRs nach Aktivierung der Agent-Schicht identifizieren.
2. Pro PR die acht Metriken aus dem Metriken-Block manuell erfassen.
3. Auditor-Verdict pro PR archivieren (Zitatpfad zur PR-Diskussion oder
   Run-Artefakt genügt).
4. Nach drei vergleichbaren PRs vorläufiges Zwischenergebnis in dieser
   Datei ergänzen — als Datenanhang, nicht als Verdict.
5. Endgültiges Verdict erst nach Erfüllung des Interpretation Budget.
6. Bei Erfüllung der Falsifikationskriterien: Blueprint revidieren oder
   `superseded` markieren; bei Bestätigung der Hypothese: Übergang zu
   Script-/CI-Rückbindung gesondert prüfen — nicht in dieser Datei
   entscheiden.
