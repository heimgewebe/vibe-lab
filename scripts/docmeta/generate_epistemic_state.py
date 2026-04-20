#!/usr/bin/env python3
"""generate_epistemic_state.py — Generiert docs/_generated/epistemic-state.md.

Erzeugt pro Experiment einen abgeleiteten epistemic_state-Report als
konsolidierte Übersichtstabelle. Alle Felder sind **derived** — sie
spiegeln vorhandene Manifest-Daten oder leiten aus Artefakt-Existenz ab.
Kein Feld wird im Manifest dupliziert.

Felder:
  - design_quality:      abgeleitet aus Existenz/Gehalt von method.md + failure_modes.md
  - execution_state:     Spiegel von experiment.execution_status
  - evidence_strength:   Spiegel von experiment.evidence_level
  - interpretation_risk: abgeleitet aus Phase 2 (interpretation_budget); bis dahin: unassessed

Referenz: docs/blueprints/blueprint-v2.md → Derived Visibility

Benötigt: pip install pyyaml
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _paths import write_if_changed  # noqa: E402

try:
    import yaml
except ImportError:
    print("ERROR: Missing dependency. Run: pip install pyyaml")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EXPERIMENTS_DIR = REPO_ROOT / "experiments"
OUTPUT = REPO_ROOT / "docs" / "_generated" / "epistemic-state.md"

# Mindestgröße (Bytes) für "hat Substanz" — Frontmatter + Überschrift allein
# liegen bei den Templates um 150–250 Bytes; alles darüber hat echten Inhalt.
_CONTENT_THRESHOLD = 300


def load_manifest(manifest_path: Path) -> dict:
    """Lädt manifest.yml; wirft bei Fehler eine Exception (fail loud).

    Ein defektes Manifest wird nicht still übersprungen — ein Visibility-
    Report, der fehlerhafte Einträge unsichtbar macht, ist epistemisch
    schlechter als kein Report.

    Strukturprüfungen:
    - YAML-Root muss ein Mapping/Object sein (kein [], "string", 42, …)
    - manifest["experiment"], falls vorhanden, muss ebenfalls ein Mapping sein
    """
    with open(manifest_path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(
            f"manifest root must be a mapping/object, got {type(data).__name__}"
        )
    exp = data.get("experiment")
    if exp is not None and not isinstance(exp, dict):
        raise ValueError(
            f"manifest.experiment must be a mapping/object, got {type(exp).__name__}"
        )
    return data


def derive_design_quality(exp_dir: Path) -> str:
    """Leitet design_quality aus method.md und failure_modes.md ab.

    - structured: beide vorhanden und mit Substanz (> Threshold)
    - partial:    genau eine vorhanden und mit Substanz
    - minimal:    keine oder beide unter Threshold
    """
    method = exp_dir / "method.md"
    failure_modes = exp_dir / "failure_modes.md"

    has_method = method.is_file() and method.stat().st_size > _CONTENT_THRESHOLD
    has_fm = failure_modes.is_file() and failure_modes.stat().st_size > _CONTENT_THRESHOLD

    if has_method and has_fm:
        return "structured"
    if has_method or has_fm:
        return "partial"
    return "minimal"


def derive_interpretation_risk(exp_dir: Path, manifest: dict) -> str:
    """Leitet interpretation_risk über eine 6-Signal-Heuristik ab.

    Signale (jedes kann den Risikowert erhöhen):
      1. evidence_sufficiency  — Hat das Experiment ausreichend Evidenz?
      2. execution_quality     — Rekonstruierte Experimente haben höheres Risiko
      3. evidence_level        — Anekdotische Evidenz erhöht Risiko
      4. adoption_basis        — Mismatch adoption_basis / execution_status
      5. interpretation_budget — Fehlendes Budget bei adopted erhöht Risiko
      6. status_consistency    — Manifest-Widersprüche erhöhen Risiko

    Rückgabe:
      - "low"    — 0-1 Signale aktiv
      - "medium" — 2-3 Signale aktiv
      - "high"   — 4+ Signale aktiv
    """
    exp = manifest.get("experiment", {})
    risk_signals = 0

    # Signal 1: evidence_sufficiency — evidence.jsonl vorhanden und nicht trivial?
    # Threshold: minimal JSONL entry is ~80+ bytes; below 50 = empty or broken
    _MIN_EVIDENCE_SIZE_BYTES = 50
    evidence_path = exp_dir / "results" / "evidence.jsonl"
    if not evidence_path.is_file():
        risk_signals += 1
    elif evidence_path.stat().st_size < _MIN_EVIDENCE_SIZE_BYTES:
        risk_signals += 1

    # Signal 2: execution_quality — rekonstruierte Experimente haben höheres Risiko
    execution_status = exp.get("execution_status", "")
    if execution_status in ("reconstructed", "designed", "not_executed"):
        risk_signals += 1

    # Signal 3: evidence_level — anekdotisch oder fehlend erhöht Risiko
    evidence_level = exp.get("evidence_level", "")
    if evidence_level in ("anecdotal", "") or evidence_level is None:
        risk_signals += 1

    # Signal 4: adoption_basis-Konsistenz — adoption_basis sollte zum
    #   execution_status passen (z.B. basis=executed → status muss executed sein)
    adoption_basis = exp.get("adoption_basis", "")
    if adoption_basis in ("executed", "replicated") and adoption_basis != execution_status:
        risk_signals += 1

    # Signal 5: interpretation_budget — bei adopted Experimenten pflicht
    status = exp.get("status", "")
    if status == "adopted":
        result_md = exp_dir / "results" / "result.md"
        has_budget = False
        if result_md.is_file():
            try:
                text = result_md.read_text(encoding="utf-8")
                has_budget = "## Interpretation Budget" in text
            except Exception:
                pass
        if not has_budget:
            risk_signals += 1

    # Signal 6: status_consistency — Widersprüche zwischen Manifest-Feldern
    #   z.B. status=adopted aber kein decision.yml, oder status=adopted ohne
    #   execution_status ∈ {executed, replicated, reconstructed}
    if status == "adopted":
        decision_path = exp_dir / "results" / "decision.yml"
        if not decision_path.is_file():
            risk_signals += 1
        elif execution_status not in ("executed", "replicated", "reconstructed"):
            risk_signals += 1

    # Risiko-Klassifikation
    if risk_signals <= 1:
        return "low"
    elif risk_signals <= 3:
        return "medium"
    else:
        return "high"


def main() -> None:
    experiments: list[dict[str, str]] = []
    manifest_errors: list[str] = []

    for manifest_path in sorted(EXPERIMENTS_DIR.glob("*/manifest.yml")):
        exp_dir = manifest_path.parent
        if exp_dir.name.startswith("_"):
            continue  # _template, _archive

        try:
            manifest = load_manifest(manifest_path)
        except Exception as exc:
            rel = manifest_path.relative_to(REPO_ROOT)
            manifest_errors.append(f"  ❌ {rel}: {exc}")
            continue

        exp = manifest.get("experiment", {})
        name = exp_dir.name
        status = exp.get("status", "—")

        experiments.append({
            "name": name,
            "status": status,
            "design_quality": derive_design_quality(exp_dir),
            "execution_state": exp.get("execution_status", "—"),
            "evidence_strength": exp.get("evidence_level", "—"),
            "interpretation_risk": derive_interpretation_risk(exp_dir, manifest),
        })

    # Tabelle bauen
    lines = [
        "<!-- GENERATED FILE — DO NOT EDIT MANUALLY -->",
        "<!-- Generated by generate_epistemic_state.py -->",
        "",
        "# Epistemic State — Experiment-Übersicht",
        "",
        "> Abgeleitete Sichtbarkeitsebene gem. [blueprint-v2.md](../blueprints/blueprint-v2.md).",
        "> Alle Felder sind **derived** — sie spiegeln Manifest-Daten oder leiten aus",
        "> Artefakt-Existenz ab. Kein Feld ist Autorfeld.",
        "",
        "| Experiment | Status | Design Quality | Execution State | Evidence Strength | Interpretation Risk |",
        "| ---------- | ------ | -------------- | --------------- | ----------------- | ------------------- |",
    ]

    for e in experiments:
        lines.append(
            f"| `{e['name']}` "
            f"| {e['status']} "
            f"| {e['design_quality']} "
            f"| {e['execution_state']} "
            f"| {e['evidence_strength']} "
            f"| {e['interpretation_risk']} |"
        )

    lines.append("")

    # Legende
    lines.extend([
        "## Legende",
        "",
        "**Design Quality** — heuristische Strukturindikation, keine semantische Qualitätsbewertung.",
        "Abgeleitet aus Vorhandensein und Mindestsubstanz von `method.md` / `failure_modes.md`",
        "(Substanz wird über eine Byte-Schwelle approximiert, nicht durch Inhaltsanalyse geprüft):",
        "- **structured** — beide Dateien vorhanden und über Mindestsubstanz-Schwelle",
        "- **partial** — genau eine Datei vorhanden und über Schwelle",
        "- **minimal** — keine Datei über Schwelle (Template-Stub oder fehlend)",
        "",
        "**Execution State** — Spiegel von `execution_status` im Manifest.",
        "",
        "**Evidence Strength** — Spiegel von `evidence_level` im Manifest.",
        "",
        "**Interpretation Risk** — abgeleitet über 6-Signal-Heuristik:",
        "- **low** — 0-1 Risikosignale aktiv (Evidenz, Execution, Budget, Konsistenz intakt)",
        "- **medium** — 2-3 Risikosignale aktiv (einige epistemische Lücken)",
        "- **high** — 4+ Risikosignale aktiv (erhebliche Interpretationsunsicherheit)",
        "",
        "Signale: evidence_sufficiency, execution_quality, evidence_level,",
        "adoption_basis-Konsistenz, interpretation_budget-Vollständigkeit, status_consistency.",
        "",
    ])

    if manifest_errors:
        print("❌ Manifest-Ladefehler — Report wird nicht geschrieben:")
        for err in manifest_errors:
            print(err)
        sys.exit(1)

    content = "\n".join(lines)
    written = write_if_changed(OUTPUT, content)
    status_sym = "✅" if written else "✔️ (unchanged)"
    print(f"{status_sym} Generated {OUTPUT.relative_to(REPO_ROOT)} ({len(experiments)} experiments)")


if __name__ == "__main__":
    main()
