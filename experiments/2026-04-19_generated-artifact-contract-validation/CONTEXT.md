title: "Kontext: Generated Artifact Contract Validation"
status: draft
canonicality: operative
---

# CONTEXT.md — Experiment-Kontext

> **Pflichtdokument für Adopt-Kandidaten.** Beschreibt den vollständigen Kontext, in dem das Experiment stattfindet.

## Ausgangslage

Das Repository hat einen Architekturwechsel fuer generierte Diagnoseartefakte vollzogen:

- Vertragsquelle in `.vibe/generated-artifacts.yml`
- Klassen: `canonical`, `derived`, `ephemeral`
- CI-Verhalten: `blocking`, `non-blocking`, `artifact-only`

Ungetestete Kernannahme: Diese Trennung reduziert tatsaechlich Drift, Reibung und kognitive Last im Tagesbetrieb.

## Umgebung

- **Tools:** GitHub Actions, make, Python 3.11, git
- **Sprache:** Mixed (Markdown, YAML, Python)
- **Projekttyp:** Policy-gesteuertes Repo mit CI-Validierung
- **Modell(e):** GPT-5.3-Codex

## Relevante Vorarbeiten

- `.vibe/generated-artifacts.yml` (Contract und Klassifikation)
- `.github/workflows/validate.yml` (job-Split: validate, derived-diagnostics, ephemeral-diagnostics)
- `docs/index.md` (Dokumentation der Diagnoseklassen und CI-Relevanz)
- `experiments/2026-04-15_agent-task-validity/` (Methodenbezug fuer Reibungs- und Review-Metriken)

## Einschränkungen

- N=2 bis N=3 PR-Durchlaeufe liefern nur fruehe Evidenz (noch keine robuste Generalisierung).
- Reale Teamlast und Reviewer-Verfuegbarkeit koennen Messwerte zu Friction verzerren.
- Messung kognitiver Last bleibt teilweise subjektiv und muss transparent dokumentiert werden.
