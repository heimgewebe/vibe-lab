# Outcome-Bound Operator Loop — S1-R2 paper successor

S1-R2 is a design-only successor to rejected S1-R1. It does not activate natural sampling.

The predecessor author revision `9e3033adb2a394fd871e0a1a30f9709afdc35321` was rejected by the terminal closeout merged through PR #349 because two material sampling defects remained:

1. source independence was not frozen, so experiment-caused candidates could be manufactured after activation;
2. identity grouping ignored Bureau's canonical legacy fallback `candidate-event-<event_id>` for candidate events without a stored `candidate_id`.

S1-R2 changes sampling semantics only at those two seams. A third predecessor incident was process-level: PR #348 was merged before all terminal exact-head review receipts were reconciled. S1-R2 freezes that failure as paper case P18 and a fail-closed design merge gate; it does not change Grabowski runtime or merge-policy authority.

The S0-R3 C/S/B/E/T/Q admission semantics remain unchanged.

This experiment asks a paper-level question only: can a natural sampling contract close both predecessor defects without introducing another post-observation degree of freedom or a new production/control surface?

No Bureau candidate is selected or consumed by this experiment. A later natural trial requires a separate revision and separate authorization after this paper gate is terminal.

Authority remains external to Vibe-Lab: Bureau owns candidate/event truth; Grabowski owns execution receipts; Git/GitHub/CI own revision truth. S1-R2 stores references and paper cases only.
