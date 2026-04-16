# Iteration 3 + 4 — Ergebnisbericht

- triggered_by: pr_iteration4_agent_task_validity
- date: 2026-04-16
- iteration: 4

## Kurzantwort auf die Leitfragen

1. **Wurden die Tasks tatsächlich ausgeführt?** Ja. Iteration 3: 6/6 Tasks (Text-Level). Iteration 4: 8/8 Tasks (Logic-Level).
2. **Gibt es erstmals echte Vergleichsdaten zwischen Control und Treatment?** Ja, über zwei Iterationen mit steigender Komplexität, aber weiterhin ohne externes Blind-Review.
3. **Reicht die Evidenz für adopted, rejected oder bleibt es inconclusive?** Inconclusive (konservativ) — Blind-Review und Replikation fehlen.
4. **Hat Iteration 4 neue Signale erzeugt?** Ja, erstmals dokumentierte Drift-Temptations. Nein, weiterhin 0 messbare Drift.

## Belegt

- Iteration-4-Set `tasks.iteration4.jsonl` enthält 8 Logic-Level-Tasks.
- Control-Arm (T1, T3, T5, T7) wurde vollständig ausgeführt, ohne Abbrüche.
- Treatment-Arm (T2, T4, T6, T8) wurde vollständig ausgeführt, mit per-Task-Protokollen.
- Task-Komplexität ist nachweislich gestiegen: isinstance-Guards, Variable-Renames, CI-Edits.
- Scope-Drift in beiden Armen: 0.
- Drift-Temptations dokumentiert: 3/4 (Control) vs 4/4 (Treatment).
- Im Treatment-Arm: jede Temptation durch Protokoll explizit geblockt.
- Treatment-Overhead: ~28% höhere Ausführungszeit.

## Plausibel

- Das Task-Protokoll macht Drift-Temptations sichtbar und blockt sie explizit.
- Ohne Protokoll wurden Temptations erst in der nachträglichen Analyse sichtbar.
- Bei höherer Komplexität (Architektur-Level) könnte der Protokoll-Effekt stärker werden.
- Der Ceiling-Effekt (0 vs 0 Drift) deutet darauf hin, dass die aktuelle Komplexität
  noch nicht ausreicht, um tatsächliche Drift zu provozieren.

## Nicht belegt

- Kein belastbarer Unterschied bei `review_comments`/Review-Friction — externes Blind-Review fehlt.
- Kein belastbarer Unterschied bei Rework — keine externen Review-Änderungen erforderlich.
- Keine Generalisierung — kein zweiter Lauf (Replikation) vorhanden.
- Keine Aussage, ob der Drift-Effekt bei höherer Komplexität auftreten würde.
- Bias-Risiko: gleicher Executor für beide Arme kennt das Experimentdesign.

## Iteration 3 vs Iteration 4 — Vergleich

| Metrik | Iteration 3 | Iteration 4 | Differenz |
|--------|-------------|-------------|-----------|
| Tasks | 6 (Text) | 8 (Logic) | Komplexität ↑ |
| Scope Drift (Control) | 0 | 0 | — |
| Scope Drift (Treatment) | 0 | 0 | — |
| Independent Changes | 0 / 0 | 0 / 0 | — |
| Abort Rate | 0% / 0% | 0% / 0% | — |
| Execution Time (C/T) | 8/14 min | 18/23 min | ↑ (komplexere Tasks) |
| Treatment Overhead | 75% | 28% | ↓ (relativer Overhead sinkt) |
| Drift-Temptations | nicht erfasst | 3/4 vs 4/4 | NEU |
| Blind Review | nein | nein (ausstehend) | — |
| Replikation | nein | nein (ausstehend) | — |

## Epistemische Lücken

1. **Blind-Review**: Ohne externen Reviewer ist Review-Friction nicht messbar.
   Status: **ausstehend, verpflichtend für Iteration 4**.

2. **Replikation**: Ohne unabhängigen zweiten Lauf keine Aussage über Reproduzierbarkeit.
   Status: **ausstehend, verpflichtend für Iteration 4**.

3. **Drift-Messung**: 0 vs 0 Drift über 14 Tasks in 2 Iterationen. Mögliche Erklärungen:
   - (a) Protokoll und kein Protokoll sind äquivalent bei dieser Komplexität
   - (b) Der Executor war zu diszipliniert (Bias)
   - (c) Tasks waren nicht komplex genug für echte Drift
   Ohne Review und Replikation kann nicht zwischen (a), (b), (c) unterschieden werden.

4. **Alternative Methodik**: Synthetische Drift-Fallen (absichtlich mehrdeutige Tasks)
   könnten Drift provozieren und wären methodisch stärker kontrolliert als „realistischere" Tasks.
