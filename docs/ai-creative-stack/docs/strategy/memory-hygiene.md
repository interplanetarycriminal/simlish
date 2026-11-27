# Memory and context hygiene

Know which kind of knowledge you are reading, and never let an old note outrank the current instruction.

## Five kinds of context, kept apart

| Kind | Example | Authority |
| --- | --- | --- |
| Current instruction and specification | The user's brief, `SPEC.md`, `DESIGN.md` | Highest |
| Project knowledge | Docs, code, a graph from [projectgraph](../../kit/projectgraph/README.md) or [Graphify](../repositories/graphify.md) | Reference |
| Approved decisions | [decisionlog](../../kit/decisionlog/README.md), `decision-log.jsonl` | Reference, with provenance |
| Unverified observations | A note from a previous session, a social-media claim | Must be verified before use |
| Temporary task state | Work-package status, scratch files | Discard when the task ends |

## Rules

- Store provenance, revision, confidence, review status and an expiry where it helps. Verify fresh or contradictory information before promoting it to reusable guidance.
- Data minimisation: record only what the next session needs. No hidden collection, no background monitoring, no secrets.
- Persistent memory is optional. An approved local decision log is enough for most projects. If you enable [Claude Mem](../repositories/claude-mem.md), turn its analytics off and decide its retention first (see [SECURITY.md](../../SECURITY.md)).
- Never suppress safety constraints or current instructions because of something remembered.
- Do not hold back an urgent, verified security fix to satisfy a cooldown rule.

See also the [persistent intelligence workflow](../workflows/persistent-intelligence.md).
