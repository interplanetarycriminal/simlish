# Independent monitoring and termination

Stop failing work early, keep what it produced, and report why.

## Limits that can be enforced

| Signal | Rule | In workledger |
| --- | --- | --- |
| Time | Each attempt has a timeout | `budget.seconds` |
| Retries | A fixed number of attempts | `retry_limit` |
| Repeated equivalent failure | Two attempts fail with identical output: stop, do not keep retrying | Tested: the always-failing package stopped after 2 attempts; the baseline used all 5 |
| No progress | A retry changes nothing and still fails: stop | Implemented |
| Scope change | Any file changed outside the package's edit scope: stop and review | Tested: the write to `ui/hacked.css` was caught; the baseline accepted it |
| Failed dependency | Do not run a package whose input failed | Tested: blocked, where the baseline ran it and failed |
| Cost and tool calls | Enforce where the environment exposes them | Not measured here; never invent readings |

## Be honest about what watches

A deterministic limit in the same process is not an independent watchdog. Say which one you have. An external monitor needs its own process, its own limits and permission to stop the work.

## When something stops

Keep checkpoints and partial artifacts, release locks, and write a blocker report: what was attempted, the evidence, and what is needed. Distinguish a failure from a cancellation. Never deploy remotely or run something costly without permission, even to finish.

## Overhead

Monitoring costs time. In the fixture, hashing the project to detect scope changes took a few milliseconds per attempt, and the governed run still finished in about half the baseline's time because it stopped wasted retries. On large projects, restrict hashing to the declared scopes.
