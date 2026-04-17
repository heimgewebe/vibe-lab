#!/usr/bin/env python3
"""generate_epistemic_state.py — Generiert docs/_generated/epistemic-state.md.

Erzeugt pro Experiment einen abgeleiteten epistemic_state-Report als
konsolidierte Übersichtstabelle. Alle Felder sind **derived** — sie
spiegeln vorhandene Manifest-Daten oder leiten aus Artefakt-Existenz ab.
Kein Feld wird im Manifest dupliziert.

Felder:
  - design_quality:        abgeleitet aus Existenz/Gehalt von method.md + failure_modes.md
  - execution_state:       Spiegel von experiment.execution_status
  - evidence_strength:     Spiegel von experiment.evidence_level
  - interpretation_risk:   heuristisch abgeleitet aus Evidenz-Existenz und -Konsistenz
  - reconciliation_state:  heuristisch abgeleitet aus Artefakt-Existenz und PR-Typ-Signalen

Heuristiken:
  interpretation_risk — bewertet, wie belastbar die epistemische Grundlage eines
  Experiments ist. Stufen:
    low:     evidence.jsonl vorhanden, ≥ 3 Einträge, execution_status konsistent
    medium:  evidence.jsonl vorhanden, aber dünn (< 3 Einträge) oder
             execution_status nicht konsistent mit Evidenzlage
    high:    kein evidence.jsonl oder Datei leer (0 Bytes / 0 gültige JSON-Zeilen)
    unknown: nicht bestimmbar (kein experiment-Block im Manifest)

  reconciliation_state — erkennt heuristisch ob ein Experiment im
  Reconciliation-Zustand ist:
    active:   reconciliation.md oder iteration*-reconciliation.md im
              artifacts/-Verzeichnis vorhanden
    inferred: execution_status ist designed/prepared, aber evidence.jsonl
              existiert mit Einträgen (Hinweis auf mögliche Inkonsistenz)
    none:     kein Reconciliation-Signal erkannt

  WICHTIG: Beide Heuristiken sind *indikativ*, nicht *wahrheitsgarantierend*.
  Sie approximieren den epistemischen Zustand auf Basis von Datei-Existenz und
  Manifest-Feldern. Falsch-positive und falsch-negative Ergebnisse sind möglich.

Referenz: docs/blueprints/blueprint-v2.md → Derived Visibility

Benötigt: pip install pyyaml
"""

import json
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

# Mindestanzahl gültiger Evidence-Einträge für "low" interpretation_risk.
_EVIDENCE_MIN_ENTRIES = 3

# Execution-Statuswerte, die eine tatsächliche Ausführung implizieren.
_EXECUTED_STATES = frozenset({"executed", "replicated", "reconstructed"})


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


def _count_evidence_entries(evidence_path: Path) -> int:
    """Zählt gültige JSON-Zeilen in einer evidence.jsonl-Datei.

    Leere Zeilen und nicht-parseable Zeilen werden übersprungen.
    Gibt 0 zurück, wenn die Datei nicht existiert oder leer ist.
    """
    if not evidence_path.is_file():
        return 0
    count = 0
    try:
        text = evidence_path.read_text(encoding="utf-8")
    except OSError:
        return 0
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            json.loads(stripped)
            count += 1
        except (json.JSONDecodeError, ValueError):
            pass
    return count


def derive_interpretation_risk(exp_dir: Path, exp: dict) -> str:
    """Leitet interpretation_risk heuristisch ab.

    Heuristik (explizit dokumentiert — indikativ, nicht wahrheitsgarantierend):

    1. Kein experiment-Block im Manifest → 'unknown'
    2. evidence.jsonl nicht vorhanden oder 0 gültige Einträge → 'high'
    3. evidence.jsonl vorhanden mit < _EVIDENCE_MIN_ENTRIES Einträgen
       ODER execution_status impliziert Ausführung aber evidence ist dünn → 'medium'
    4. evidence.jsonl vorhanden mit ≥ _EVIDENCE_MIN_ENTRIES Einträgen
       UND execution_status konsistent → 'low'

    Konsistenz-Check: execution_status ∈ {executed, replicated, reconstructed}
    erfordert vorhandene Evidenz für 'low'.
    """
    if not exp:
        return "unknown"

    evidence_path = exp_dir / "results" / "evidence.jsonl"
    entry_count = _count_evidence_entries(evidence_path)
    execution_status = exp.get("execution_status", "")

    # Kein Evidence → high risk
    if entry_count == 0:
        return "high"

    # Konsistenz-Prüfung: executed-Status mit dünner Evidenz → medium
    claims_execution = execution_status in _EXECUTED_STATES
    is_thin = entry_count < _EVIDENCE_MIN_ENTRIES

    if is_thin:
        return "medium"

    # Inkonsistenz: Evidenz vorhanden aber Status sagt "nicht ausgeführt"
    if not claims_execution and entry_count > 0:
        return "medium"

    return "low"


def derive_reconciliation_state(exp_dir: Path, exp: dict) -> str:
    """Leitet reconciliation_state heuristisch ab.

    Heuristik (explizit dokumentiert — indikativ, nicht wahrheitsgarantierend):

    1. 'active': Im artifacts/-Verzeichnis existiert eine Datei namens
       reconciliation.md oder passend zu iteration*-reconciliation.md.
       Dies ist ein starkes Signal für einen aktiven oder abgeschlossenen
       Reconciliation-Prozess.

    2. 'inferred': execution_status ist designed oder prepared, aber
       evidence.jsonl existiert mit gültigen Einträgen. Dies deutet auf
       eine mögliche Inkonsistenz hin (Evidenz ohne passenden Execution-Claim).

    3. 'none': Kein Reconciliation-Signal erkannt.
    """
    artifacts_dir = exp_dir / "artifacts"

    # Signal 1: Explizite Reconciliation-Artefakte
    if artifacts_dir.is_dir():
        for f in artifacts_dir.iterdir():
            if not f.is_file():
                continue
            name_lower = f.name.lower()
            if name_lower == "reconciliation.md":
                return "active"
            if name_lower.endswith("-reconciliation.md") and name_lower.startswith("iteration"):
                return "active"

    # Signal 2: Inkonsistenz — Evidenz ohne Execution-Claim
    execution_status = exp.get("execution_status", "")
    if execution_status in ("designed", "prepared"):
        evidence_path = exp_dir / "results" / "evidence.jsonl"
        if _count_evidence_entries(evidence_path) > 0:
            return "inferred"

    return "none"


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

        interpretation_risk = derive_interpretation_risk(exp_dir, exp)
        reconciliation_state = derive_reconciliation_state(exp_dir, exp)

        # CI-Warnung: high interpretation_risk bei execution_status ∈ executed-Gruppe
        execution_status = exp.get("execution_status", "")
        if interpretation_risk == "high" and execution_status in _EXECUTED_STATES:
            print(
                f"  ⚠️  {name}: interpretation_risk=high but "
                f"execution_status={execution_status} — evidence may be missing or empty"
            )

        experiments.append({
            "name": name,
            "status": status,
            "design_quality": derive_design_quality(exp_dir),
            "execution_state": execution_status or "—",
            "evidence_strength": exp.get("evidence_level", "—"),
            "interpretation_risk": interpretation_risk,
            "reconciliation_state": reconciliation_state,
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
        ">",
        "> **Interpretation Risk** und **Reconciliation State** sind *heuristisch abgeleitet*",
        "> und *indikativ* — sie zeigen, wo das Repo sich selbst noch nicht trauen sollte,",
        "> sind aber keine Wahrheitsgarantie. Siehe Legende für Details.",
        "",
        "| Experiment | Status | Design Quality | Execution State | Evidence Strength | Interpretation Risk | Reconciliation |",
        "| ---------- | ------ | -------------- | --------------- | ----------------- | ------------------- | -------------- |",
    ]

    for e in experiments:
        lines.append(
            f"| `{e['name']}` "
            f"| {e['status']} "
            f"| {e['design_quality']} "
            f"| {e['execution_state']} "
            f"| {e['evidence_strength']} "
            f"| {e['interpretation_risk']} "
            f"| {e['reconciliation_state']} |"
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
        "**Interpretation Risk** — heuristisch abgeleitet aus Evidenz-Existenz,",
        "Evidenz-Dichte und Konsistenz mit `execution_status`. *Indikativ, nicht wahrheitsgarantierend.*",
        "- **low** — `evidence.jsonl` vorhanden mit ≥ 3 gültigen Einträgen, `execution_status` konsistent",
        "- **medium** — Evidenz vorhanden aber dünn (< 3 Einträge) oder inkonsistent mit Execution-Claim",
        "- **high** — kein `evidence.jsonl` oder Datei leer (0 gültige JSON-Zeilen)",
        "- **unknown** — nicht bestimmbar (kein `experiment`-Block im Manifest)",
        "",
        "**Reconciliation** — heuristisch abgeleitet aus Artefakt-Existenz.",
        "*Indikativ, nicht wahrheitsgarantierend.*",
        "- **active** — explizites Reconciliation-Artefakt gefunden (`reconciliation.md`",
        "  oder `iteration*-reconciliation.md` in `artifacts/`)",
        "- **inferred** — mögliche Inkonsistenz: `execution_status` ist `designed`/`prepared`,",
        "  aber `evidence.jsonl` enthält Einträge",
        "- **none** — kein Reconciliation-Signal erkannt",
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
