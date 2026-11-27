# workledger

Plans, runs and reconciles bounded work packages under a deterministic monitor, and records what was planned against what actually happened.

**Stands in for:** the V7 strategy layer (spec-first packages, bounded delegation, independent monitoring, plan/action reconciliation, recorded alternatives), as one tested, framework-free tool. See [docs/strategy](../../docs/strategy/README.md).

## What it does

| Command | Does |
| --- | --- |
| `check work-packages.json` | Validates every package. Rejects dependency cycles, unknown dependencies, empty edit scopes and packages without acceptance checks. Schedules the rest into waves: independent packages share a wave unless their edit scopes overlap, in which case they are serialized. |
| `run work-packages.json --root DIR` | Runs waves in order. Each attempt hashes the project before and after, runs the command, then the acceptance checks, and appends a ledger entry (see below). |
| `run ... --baseline` | The comparison: file order, every retry used, no scope checks, no early stop, dependents run regardless. |
| `decide decision-log.jsonl ...` | Records a decision with at least two alternatives, the chosen one, rationale, evidence, uncertainty and a review trigger. |
| `reconcile execution-ledger.jsonl` | The final planned-versus-observed status of every package. |

On each attempt, `run` records the planned effect, the observed effect, the changed paths, the validation result and the deviation. The monitor stops a package early in these cases:

- **Out of scope:** it changed a file outside its `edit_scope`. That is a deviation and stops it.
- **Repeated failure:** two attempts failed with byte-identical output.
- **No progress:** a retry changed nothing and still failed.
- **Budget:** it exceeded `budget.seconds` on an attempt, or `retry_limit` overall.

A package whose dependency did not finish is blocked, not run. These are deterministic limits, not an independent watchdog process: the docs say so rather than claim otherwise.

Formats follow [registry/contracts](../../registry/contracts/): `work-packages.schema.json`, `execution-ledger.schema.json` and `decision-log.schema.json`.

## Test

```sh
python test.py
```

The test builds a seven-package project with planted problems: a dependent chain, two packages sharing a scope, a package that always fails the same way, a package that writes outside its scope, a dependent of a failure, and a package that fails once and then succeeds. It runs the baseline and the governed process on identical copies. Result on 2026-11-27: **pass, 17 of 17 checks**.

| Measure | Baseline | Governed |
| --- | --- | --- |
| Attempts | 16 | 8 |
| Total time | 3.6 s | 2.0 s |
| Write outside scope (`ui/hacked.css`) | Missed | Caught and stopped |
| Identical failure | Retried to the limit | Stopped after 2 attempts |
| Dependent of a failure | Ran and failed | Blocked |
| Fails once, then succeeds | Done | Done |

The test also checks cycle detection, rejection of unverifiable packages, scope-overlap serialisation, the refusal of a decision with one alternative, and that every ledger, decision and package file validates against its contract. The measured comparison is written to [out/strategy-evaluation.md](out/strategy-evaluation.md).

## Limits

- One machine, one synthetic project. It shows the mechanism works, not that a real team will see the same savings.
- Hashing the whole project costs time on large trees; restrict snapshots to declared scopes there.
- Packages run sequentially within a wave. The waves say what may run in parallel; running them in parallel is left to the caller.
