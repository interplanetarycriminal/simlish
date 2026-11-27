# Strategy evaluation

Compare a governed process with direct execution on the same tasks. Report only what was measured; mark everything else as an estimate or as not measured.

| Field | Value |
| --- | --- |
| Tasks (work-package file) | |
| Inputs (same for both runs) | |
| Machine and versions | |
| Date | |

## Results

| Measure | Direct execution | Governed | How it was measured |
| --- | --- | --- | --- |
| Acceptance checks passed | | | |
| Attempts and retries | | | ledger line count |
| Wall time | | | |
| Cost, if actually metered | | | |
| Scope deviations caught | | | ledger `deviation_reason` |
| Failures stopped early | | | |
| Work wasted on blocked dependents | | | |

## Failure modes seen

## Trade-offs and limits

What the comparison does not show, such as other machines, larger projects or real teams.

## Decision

Keep, change or drop the governed process for this kind of task, with a review trigger. Record it in `decision-log.jsonl`.

A filled-in example: [kit/workledger/out/strategy-evaluation.md](../kit/workledger/out/strategy-evaluation.md).
