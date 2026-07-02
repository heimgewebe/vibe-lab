---
title: "Playbook: Operator Lab Loop"
status: active
canonicality: operative
schema_version: "0.1.0"
created: "2026-07-01"
updated: "2026-07-01"
author: "heimgewebe"
triggered_by: "user-request-vibe-lab-operator-lab-loop-2026-07-01"
relations:
  - type: references
    target: pr-run-evidence-pack.md
  - type: references
    target: pr-context-capture.md
  - type: references
    target: plan-execution-checklist.md
  - type: references
    target: ../roadmap.md
  - type: references
    target: ../../experiments/2026-07-01_operator-lab-loop/manifest.yml
  - type: references
    target: ../../experiments/2026-06-10_pr-agent-context-comparison-series/pilot-v1.yml
    reason: "The operator loop should feed the frozen PR-context pilot, not bypass it."
tags:
  - playbook
  - operator
  - evidence
  - pr
  - agent-workflow
---

# Playbook: Operator Lab Loop

> **Zweck:** Vibe-Lab wird als Messrahmen fuer echte Repo-, PR- und Agentenarbeit genutzt. Es erzeugt keine Freigabe, keinen Merge und kein Erfolgsverdikt. Es macht sichtbar, welche Arbeitsweise geholfen hat, welche Reibung entstand und welche Claims belegt sind.

## 1. Dialektischer Kern

### These

Vibe-Lab soll reale Arbeit verbessern: PRs, Reviews, Agenten-Delegation, Operator-Entscheidungen und Handoffs werden vergleichbarer, wenn jeder relevante Arbeitslauf eine kleine, pruefbare Spur bekommt.

### Antithese

Zu viel Labor macht Arbeit langsamer. Ein zusaetzlicher Validator, eine weitere Pflichtdatei oder ein weiterer Review-Gate kann mehr Reibung erzeugen als er entfernt.

### Synthese

Der Operator Lab Loop ist bewusst klein: Er dokumentiert nur Entscheidung, Kontext, Evidence, Reibung und naechste Konsequenz. Er ist ein Nutzungsprotokoll, kein neues Kontrollregime.

## 2. Alternative Sinnachse

Nicht fragen: "Wie bauen wir Vibe-Lab weiter aus?"

Sondern fragen: "Welche Unsicherheit in unserer echten Arbeit muss kleiner werden?"

Primaere Unsicherheit:

> Kann ich einem Agenten-, Tool- oder Review-Ergebnis trauen, und warum?

Sekundaere Unsicherheit:

> War der zusaetzliche Prozess selbst nuetzlich oder nur methodischer Schmuck?

## 3. Ausloeser

Der Loop wird genutzt, wenn mindestens eine Bedingung zutrifft:

- ein PR-Review oder PR-Rework beeinflusst eine Entscheidung;
- Codex, Claude, Aider, agy, Grabowski oder Bureau werden fuer Repo-Arbeit eingesetzt;
- ein starker Claim entstehen koennte, zum Beispiel "CI gruen", "Agent hat korrekt umgesetzt", "Review war unabhaengig", "Kontext hat geholfen";
- eine neue Arbeitsweise dauerhaft uebernommen werden soll;
- ein Operator-Fehler, eine Friktion oder ein Scope-Drift sichtbar wurde.

Nicht nutzen fuer triviale Aenderungen ohne Claim, Entscheidung oder Lernwert.

## 4. Minimaler Ablauf

1. **Praemissencheck:** Was muesste wahr sein, damit der Arbeitsmodus sinnvoll ist?
2. **Condition festhalten:** baseline, Vibe-Lab-Handoff, Lenskit-Handoff, decision-first checklist oder other.
3. **Steuerboard-Signal lesen:** `steuerboard operator report --branch-warning-threshold 5 --json` als Nutzungsprobe; kein Gate.
4. **Run Card schreiben:** kleine YAML-Card unter `artifacts/run-*/run-card.yml`.
5. **Evidence binden:** kleine repo-lokale Artefakte oder stabile Referenzen. Keine Loghalde.
6. **Reibung zaehlen:** Zeit, Korrektur, Nacharbeit, falsche Claims, Entscheidungsaufwand.
7. **Entscheiden:** adopt, iterate, defer, reject oder no_decision.
8. **Rueckfuehren:** Nur bei wiederholtem Nutzen in Playbook, Instruction Block, Agent-Regel oder Bureau-Kandidat uebertragen.

## 4.1 Ablage-Regel fuer Run Cards

Wenn eine Operator-Lab-Run-Card noetig ist, ist die Standard-Zielstruktur im Vibe-Lab:

```text
experiments/2026-07-01_operator-lab-loop/artifacts/run-XXX-<slug>/run-card.yml
```

Dazu gehoert in derselben Run-Directory ein `run_meta.json`, sobald der Run als ausgefuehrter Operator-Lab-Arbeitslauf dokumentiert wird.

`raw-vibes/` ist nur Intake: Rohnotizen, erste Beobachtungen oder ungeformte Ideen duerfen dort landen. Ein PR-Body darf `raw-vibes/...` aber nicht als finalen Operator-Lab-Nachweis verwenden, wenn der Trigger-Check `Run Card nötig? yes` ergeben hat. In diesem Fall muss die Rohnotiz entweder vor dem Merge in eine strukturierte Run Card ueberfuehrt werden oder der PR muss sie ausdruecklich als `raw/intake` markieren und einen Follow-up zur Strukturierung nennen.

PR-Body-Regel:

```text
Operator-Lab-Run: vibe-lab: experiments/2026-07-01_operator-lab-loop/artifacts/run-XXX-<slug>/run-card.yml
```

Nur wenn keine Run Card noetig ist:

```text
Operator-Lab-Run: not applicable — <kurzer Grund>
```

Repo-lokale Sicherung: `make validate-operator-lab-run-cards` prueft, dass `raw-vibes/operator-lab-run-*.md` nicht ohne strukturierte Run-Card-Folge im Vibe-Lab bleibt. Dieser Guard ist eng: Er validiert Raw-Note-Linkage, nicht jeden historischen Operator-Lab-Artefaktstil und nicht GitHub-PR-Bodies.

## 5. Run Card Mindestfelder

```yaml
schema_version: "0.1.0"
run_id: "run-YYYYMMDD-short-name"
date: "YYYY-MM-DD"
operation: "kurze Beschreibung"
target_repo: "repo oder Pfad"
condition: "baseline | vibe_lab_handoff | lenskit_handoff | decision_first | other"
operator_tooling:
  - "ChatGPT"
  - "Grabowski"
claims:
  - claim: "enger Claim"
    status: "observed | plausible | missing_evidence | not_claimed"
    evidence:
      - path: "repo-lokaler Pfad oder stabile Referenz"
        evidence_status: "repo_local | external_verified | external_unverified | missing_evidence"
metrics:
  scope_drift_count: 0
  unsupported_claim_count: 0
  missing_locator_count: 0
  validation_gap_count: 0
  review_friction_count: 0
  rework_count: 0
  false_block_count: 0
  task_completion_time_observed: "not_measured"
steuerboard_probe:
  useful_signal: "..."
  changed_decision: "yes | no"
  noise: "low | medium | high"
bureau_bridge:
  create_or_update_candidate: false
  reason: "..."
decision: "adopt | iterate | defer | reject | no_decision"
does_not_establish:
  - "condition_superiority"
  - "general_agent_quality"
  - "adoption_readiness"
```

## 6. Claim-Grenzen

Belegt:

- Ein Befehl lief, wenn Output, Exit-Code oder stabile externe Evidence vorliegt.
- Ein Review-Kommentar existiert, wenn ein Review-Export oder eine stabile Referenz vorliegt.
- Ein Scope-Drift wurde beobachtet, wenn geaenderte Dateien, erwartete Zielpfade und Abweichung dokumentiert sind.

Plausibel:

- Eine Arbeitsweise half, wenn weniger Rework oder weniger Review-Friction beobachtet wurde, aber nur in einem Run.
- Ein Handoff war nuetzlich, wenn der Agent weniger Rueckfragen oder weniger falsche Claims produzierte.

Nicht behauptbar:

- "Besser als Alternative" ohne Vergleichsrun.
- "Agent ist zuverlaessig" aus einem erfolgreichen Run.
- "Vibe-Lab beweist Nutzen" ohne replizierte Outcome-Evidence.
- "Bureau soll automatisch priorisieren" ohne Rueckkopplung aus mindestens drei Runs.

## 7. Bureau-Bruecke

Bureau darf Operator-Lab-Ergebnisse als Priorisierungs- oder Frontier-Signal nutzen, aber Vibe-Lab bleibt Quelle fuer methodische Evidence.

Bureau wird erst beruehrt, wenn eine dieser Bedingungen wahr ist:

- mindestens drei Operator-Lab-Runs zeigen dieselbe Reibungsklasse;
- ein Run erzeugt einen klaren Folge-Task fuer ein anderes Repo;
- ein wiederkehrender Operator-Engpass braucht systemische Priorisierung.

Bis dahin gilt:

- keine Bureau-Mutation nur zur Dokumentations-Schoenheit;
- kein Bureau-Kandidat ohne Vibe-Lab-Run-Card;
- Bureau darf zusammenfassen und priorisieren, aber keine Vibe-Lab-Claims erhoehen.

## 8. Stop-Regeln

Den Loop abbrechen oder kuerzen, wenn:

- die Dokumentation laenger wird als die eigentliche Aenderung;
- keine Entscheidung, kein Claim und keine Reibung vorliegt;
- Evidence nur aus Selbstbericht besteht und trotzdem als PASS wirken wuerde;
- der Loop selbst eine Blockade erzeugt.

## 9. Erste Umsetzung

Der erste verankerte Nutzungsfall ist `experiments/2026-07-01_operator-lab-loop/`.

Dieser Run beweist nicht, dass der Operator Lab Loop besser ist. Er beweist nur, dass der Loop als leichtgewichtige Repo-Spur angelegt und mit den bestehenden PR-Evidence-Regeln kompatibel dokumentiert werden kann.

## 10. Optimierungsziel

Was: Vibe-Lab als reale Operator-Feedbackschleife nutzbar machen.

Wie: kleine Run Cards statt grosser neuer Validatoren.

Wodurch: bestehende Evidence-Pack-, PR-Kontext- und Roadmap-Mechanik wiederverwenden.

Wirkung: weniger Overclaiming, klarere Delegationsentscheidungen, reproduzierbare Lernspuren.

Nebenwirkung: zusaetzliche Dokumentationsarbeit. Deshalb bleibt der Loop opt-in und muss Reibung sichtbar machen.
