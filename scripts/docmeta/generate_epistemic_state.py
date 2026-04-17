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
  - interpretation_risk:   mehrdimensionale Heuristik (siehe unten)
  - reconciliation_state:  heuristisch abgeleitet aus Artefakt-Existenz

Heuristiken:

  interpretation_risk — bewertet, wo das Repo seinen eigenen Claims epistemisch
  misstrauen sollte. Kombiniert mehrere Signale:

    Eingangssignale:
      1. Evidence Sufficiency:  evidence.jsonl Existenz + Anzahl parsebarer JSON-Objekte
      2. Execution Quality:     execution_status — reconstructed ist epistemisch
                                schwächer als executed/replicated
      3. Evidence Level:        evidence_level — anecdotal ist schwächer als
                                experimental/replicated
      4. Adoption Basis:        bei adopted: adoption_basis=reconstructed erhöht Risiko
      5. Interpretation Budget: bei adopted: Fehlen des Budget-Blocks in result.md
                                erhöht Risiko
      6. Status Consistency:    execution_status beansprucht keine Ausführung,
                                aber evidence.jsonl hat Einträge → erhöht Risiko

    Stufen:
      low:     hinreichende Evidenz, execution_status ∈ {executed, replicated},
               evidence_level ≥ experimental, keine strukturellen Schwächen
      medium:  Evidenz vorhanden, aber mindestens ein Risikosignal aktiv
               (z.B. reconstructed, anecdotal, dünne Evidenz, adopted ohne Budget)
      high:    keine Evidenz, oder schwerwiegende strukturelle Schwäche
      unknown: nicht bestimmbar (kein experiment-Block im Manifest)

  reconciliation_state — erkennt heuristisch ob ein Experiment im
  Reconciliation-Zustand ist. Basiert ausschließlich auf Artefakt-Existenz
  und Manifest-Inkonsistenz:
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
import re
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

# Mindestanzahl gültiger Evidence-Einträge für hinreichende Evidenz.
_EVIDENCE_MIN_ENTRIES = 3

# Execution-Statuswerte, die eine tatsächliche artefaktbelegte Ausführung
# implizieren und epistemisch gleichwertig behandelt werden.
_ANY_EXECUTION_STATES = frozenset({"executed", "replicated", "reconstructed"})

# Interpretation Budget: Marker im result.md
_BUDGET_SECTION_RE = re.compile(r"^##\s+Interpretation Budget", re.MULTILINE)


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
    """Zählt syntaktisch parsebare JSON-Objekte in einer evidence.jsonl-Datei.

    Nur Zeilen, die nach json.loads() ein dict ergeben, werden gezählt.
    Primitive Werte, Listen und nicht-parsebare Zeilen werden übersprungen.
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
            parsed = json.loads(stripped)
            if isinstance(parsed, dict):
                count += 1
        except (json.JSONDecodeError, ValueError):
            pass
    return count


def _has_interpretation_budget(exp_dir: Path) -> bool:
    """Prüft ob results/result.md einen ``## Interpretation Budget``-Block enthält.

    Prüft nur Existenz des Abschnitts-Headers, nicht inhaltliche Qualität —
    das ist Aufgabe von validate_interpretation_budget.py.
    """
    result_md = exp_dir / "results" / "result.md"
    if not result_md.is_file():
        return False
    try:
        text = result_md.read_text(encoding="utf-8")
    except OSError:
        return False
    return bool(_BUDGET_SECTION_RE.search(text))


def derive_interpretation_risk(exp_dir: Path, exp: dict) -> str:
    """Leitet interpretation_risk heuristisch ab.

    Mehrdimensionale Heuristik — kombiniert sechs Signale zu einer Risikostufe.
    Explizit dokumentiert, indikativ, nicht wahrheitsgarantierend.

    Signale (jedes kann das Risiko erhöhen):

      1. Evidence Sufficiency
         - Keine Evidenz (0 parsebare JSON-Objekte) → high
         - Dünne Evidenz (< _EVIDENCE_MIN_ENTRIES JSON-Objekte) → +risk

      2. Execution Quality
         - reconstructed ist epistemisch schwächer als executed/replicated
         - reconstructed → +risk

      3. Evidence Level
         - anecdotal ist schwächer als experimental/replicated
         - anecdotal → +risk
         - experimental und replicated erzeugen kein zusätzliches Risikosignal

      4. Adoption Basis
         - adopted + adoption_basis=reconstructed → mindestens medium

      5. Interpretation Budget (nur bei adopted)
         - adopted ohne ## Interpretation Budget in result.md → +risk

      6. Status Consistency
         - execution_status beansprucht keine Ausführung, aber Evidenz vorhanden → +risk

    Aggregation:
      Risiko-Signale werden gezählt.
      - Bei 0 Signalen → low
      - Bei 1–2 Signalen → medium
      - Bei ≥ 3 Signalen → high
      - Bei fehlendem Evidence (0 Einträge) → high (unabhängig von anderen Signalen)
      - Kein exp-Block → unknown
    """
    if not exp:
        return "unknown"

    evidence_path = exp_dir / "results" / "evidence.jsonl"
    entry_count = _count_evidence_entries(evidence_path)
    execution_status = exp.get("execution_status", "")
    evidence_level = exp.get("evidence_level", "")
    status = exp.get("status", "")
    adoption_basis = exp.get("adoption_basis", "")

    # Kein Evidence → high risk (stärkstes negatives Signal)
    if entry_count == 0:
        return "high"

    # Risiko-Signale sammeln
    risk_signals = 0

    # Signal 1: Dünne Evidenz
    if entry_count < _EVIDENCE_MIN_ENTRIES:
        risk_signals += 1

    # Signal 2: Execution Quality — reconstructed ist epistemisch schwächer
    if execution_status == "reconstructed":
        risk_signals += 1

    # Signal 3: Evidence Level — anecdotal ist schwächer
    if evidence_level == "anecdotal":
        risk_signals += 1

    # Signal 4: Adoption Basis — adopted + reconstructed = epistemisch fragil
    if status == "adopted" and adoption_basis == "reconstructed":
        risk_signals += 1

    # Signal 5: Interpretation Budget (nur bei adopted Experimenten)
    if status == "adopted" and not _has_interpretation_budget(exp_dir):
        risk_signals += 1

    # Signal 6: Inkonsistenz — execution_status sagt "nicht ausgeführt" trotz Evidenz
    if execution_status not in _ANY_EXECUTION_STATES and entry_count > 0:
        risk_signals += 1

    # Aggregation
    if risk_signals >= 3:
        return "high"
    if risk_signals >= 1:
        return "medium"
    return "low"


def derive_reconciliation_state(exp_dir: Path, exp: dict) -> str:
    """Leitet reconciliation_state heuristisch ab.

    Heuristik (explizit dokumentiert — indikativ, nicht wahrheitsgarantierend).
    Basiert ausschließlich auf Artefakt-Existenz und Manifest-Inkonsistenz:

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

        # CI-Warnung: high interpretation_risk bei execution_status, die Ausführung beansprucht
        execution_status = exp.get("execution_status", "")
        if interpretation_risk == "high" and execution_status in _ANY_EXECUTION_STATES:
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
        "> und *indikativ* — sie zeigen, wo das Repo seinen eigenen Claims epistemisch",
        "> misstrauen sollte. Keine Wahrheitsgarantie. Siehe Legende für Details.",
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
        "**Interpretation Risk** — mehrdimensionale Heuristik, die signalisiert,",
        "wo das Repo seinen eigenen Claims epistemisch misstrauen sollte.",
        "*Indikativ, nicht wahrheitsgarantierend.* Kombiniert folgende Signale:",
        "- Evidence Sufficiency (Existenz und Dichte von `evidence.jsonl`)",
        "- Execution Quality (`execution_status` — `reconstructed` erhöht Risiko)",
        "- Evidence Level (`anecdotal` erhöht Risiko, `replicated` ist neutral)",
        "- Adoption Basis (`adopted` + `adoption_basis: reconstructed` erhöht Risiko)",
        "- Interpretation Budget (bei `adopted`: Fehlen des Blocks erhöht Risiko)",
        "",
        "Stufen:",
        "- **low** — keine Risiko-Signale aktiv",
        "- **medium** — mindestens ein Risiko-Signal aktiv",
        "- **high** — keine Evidenz vorhanden, oder mehrere Risiko-Signale",
        "- **unknown** — nicht bestimmbar (kein `experiment`-Block im Manifest)",
        "",
        "**Reconciliation** — heuristisch abgeleitet aus Artefakt-Existenz",
        "und Manifest-Inkonsistenz. *Indikativ, nicht wahrheitsgarantierend.*",
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
