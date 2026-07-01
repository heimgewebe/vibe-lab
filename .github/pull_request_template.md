## Änderungszusammenfassung
<!-- 2–4 Zeilen: Was wurde geändert und warum? -->

## Änderungstyp
- [ ] Dokumentation
- [ ] Contract / Schema
- [ ] Guard / Validator / Test
- [ ] Experiment-Artefakt / Run-Bundle
- [ ] Policy / Governance
- [ ] Tooling / CI
- [ ] Generierte Artefakte nur aktualisiert

## Berührte Pfade
<!-- Konkrete Pfade, keine Platzhalter (`.../<Pfad>`). z. B. docs/, scripts/, .github/workflows/ -->

## Scope / Nicht-Ziele
<!-- Was ist bewusst in Scope, was explizit out of scope?
     Dieser Abschnitt ist Review-Kontext, kein Ersatz für run-lokale Evidence-Artefakte. -->

## Operator Lab Run

Operator-Lab-Run: <!-- vibe-lab: <pfad> oder not applicable - <kurzer Grund> -->

## Validierung

Für jeden Check unten ein Evidence Artifact angeben (repo-local, CI-Artifact oder
extern verifiziert). `external_verified` muss stabiles `source`/`ref` und `sha256`
enthalten. Keine großen Roh-Logs ins Repo einchecken.

Wenn ein Check nicht relevant ist: Verdict `OUT_OF_SCOPE`.
Wenn ein relevanter Check nicht ausgeführt oder nicht belegt ist: Evidence Status
`missing_evidence` und Verdict `MISSING_EVIDENCE`.
Nie `PASS` ohne archivierte Evidenz setzen.

| Check | Evidence | Evidence Status | Verdict | Begründung |
|---|---|---|---|---|
| `make validate` |  |  |  |  |
| Zielgerichtete Tests |  |  |  |  |
| CI-Ergebnis |  |  |  |  |
| Agent-/Auditor-/Critic-Review, falls behauptet |  |  |  |  |

## Claims und Evidence

| Claim | Claim Type | Evidence Artifact | Evidence Status | Verdict |
|---|---|---|---|---|
|  |  |  |  |  |

**Evidence Status values** (lowercase): `repo_local`, `ci_artifact`,
`external_verified`, `derived_from_auditor_output`, `missing_evidence`,
`external_unverified`, `self_reported`, `unknown`.

**Verdict values** (uppercase): `PASS`, `MISSING_EVIDENCE`, `CLAIM_NOT_PROVEN`,
`CONTRADICTION`, `OUT_OF_SCOPE`, `NOT_REPRODUCIBLE`.

**Claim Type values / examples**: `command_result`, `test_result`, `ci_result`,
`critic_usage`, `auditor_usage`, `agent_usage`.

**Regeln:**
- Keine Testanzahl-Behauptung ohne Test-Output-Evidence-Artifact.
- Keine CI-Erfolgsbehauptung ohne CI-Evidenz.
- Kein `make validate`-`PASS` ohne archivierten Command-Output.
- Keine Critic-/Auditor-/Agent-Usage-Behauptung ohne archivierten Reviewer- oder Agent-Output.
- `missing_evidence`, `external_unverified`, `self_reported` und `unknown` dürfen
  `PASS` bei Prozess- oder Ergebnis-Claims nicht stützen.
- Claims ohne Evidenz müssen `MISSING_EVIDENCE` oder `CLAIM_NOT_PROVEN` sein.

## Risiko / Nicht erledigt
<!-- Bekannte Grenzen, Follow-ups, bewusst zurückgestellte Punkte -->

## Review-Hinweise
<!-- Hinweise für Reviewende (Kontext, Prüfpunkte, Trade-offs) -->
