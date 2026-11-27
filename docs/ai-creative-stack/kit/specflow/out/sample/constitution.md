# Project constitution

The rules every spec, plan and task in this project follows. Change them only by an owner decision
recorded in the decision log.

## Precedence

1. The current instruction from the owner.
2. Project policy and security rules.
3. The approved spec.
4. The decision log (approved entries only).
5. Retrieved memory and notes.

Retrieved memory never overrides the current instruction, project policy or security rules.
When two sources conflict, follow the higher one and report the conflict with both sources.

## Articles

### I. Smallest coherent toolchain
Use the existing stack first. Add a tool only when it closes a documented gap in the spec.

### II. Test-first traceability
Every acceptance criterion has at least one task and one automated check. Every task names the
criterion it serves.

### III. Evidence over claims
Say "tested" only for what was run. Record the command, version and result for each quality gate.

### IV. Privacy
Nothing leaves the machine unless the owner approved the destination. No secrets in specs,
plans, tasks or logs.

### V. One authority
One owner per asset, timeline, specification and design document.

## Governance

- Open questions are written as [NEEDS CLARIFICATION: ...] and answered by the owner with `clarify`.
- The owner approves the spec before implementation starts.
- `analyze` must pass before implementation and again before release.
