# Bounded decomposition and delegation

Split work by independently verifiable artifact, not by a target number of agents.

## A work package

Every package has a stable id, its parent goal, approved inputs, expected outputs, dependencies, an owner, an **edit scope** (the files it may change), acceptance checks, a budget, a retry limit and a fallback. The [contract](../../registry/contracts/work-packages.schema.json) lists the fields; [workledger](../../kit/workledger/README.md) rejects a package with no acceptance check or an empty edit scope.

## Parallel or serial

- **Parallel:** packages with no dependency between them and no overlapping edit scopes.
- **Serial:** anything that shares files, or any critical handoff. workledger's `check` computes this: in its test, two independent packages that both write `assets/*` are placed in separate waves automatically.
- **Never:** an unbounded tree of workers, or several workers editing one file.

Workers may propose changes; the designated owner validates the combined result. If the environment has no real workers, run the stages one after another and say so.

## Context for each worker

Give each worker the original brief, the constraints that apply to its package, its inputs and its edit scope. Do not pass private context it does not need.

## Is delegation worth it?

Only if quality or delivery improves. Compare against direct execution on the same task with the [strategy evaluation template](../../templates/strategy-evaluation.md). If the overhead outweighs the gain, do it directly.

## Example: one film, five packages

| Package | Edit scope | Depends on |
| --- | --- | --- |
| Shot list and timing | `film/plan/*` | — |
| Scene 1 page | `film/scenes/s1.*` | Shot list |
| Scene 2 page | `film/scenes/s2.*` | Shot list |
| Render and encode | `film/out/*` | Scenes 1 and 2 |
| Review report | `film/report.md` | Render |

Scenes 1 and 2 run in parallel; the render waits for both; one owner reviews the master.
