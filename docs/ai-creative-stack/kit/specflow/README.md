# specflow

A small spec-driven flow: constitution, spec, clarifications, plan, tasks, and a consistency check. It is our own code, written from first principles. Python standard library only. No model, no network.

Stands in for: [Spec Kit](../../docs/repositories/spec-kit.md) (`specify init` and the `/speckit.specify`, `clarify`, `plan`, `tasks` and `analyze` steps). See [persistent project intelligence](../../docs/workflows/persistent-intelligence.md).

## Usage

```sh
python specflow.py init <dir>                                   # constitution.md + specs/
python specflow.py specify "Artists can upload a GLB model, preview it in a Three.js viewer, and export a validated copy with a manifest" --root <dir>
python specflow.py clarify <dir>/specs/001-.../                 # list open questions
python specflow.py clarify <dir>/specs/001-.../ --answer "Q1=..." --answer "Q2=..."
python specflow.py plan <spec> [--catalogue <catalogue root>]
python specflow.py tasks <spec>
python specflow.py analyze <spec>                               # exits 1 on gaps
python specflow.py approve <spec> --by "project owner"          # only when analyze passes
```

`<spec>` is the spec folder or its `spec.md`. Errors exit 2.

## What each step writes

- **init**: `constitution.md` with the precedence order (current instruction, policy and security, approved spec, decision log, retrieved memory), five articles and governance rules.
- **specify**: `specs/NNN-slug/spec.md`. The description is split into steps at commas, semicolons and "then". Each step becomes a user story `USn` with two criteria: `ACn.1` (the happy path) and `ACn.2` (invalid input stops with a clear error). The actor comes from "X can ...", the benefit from "so that ...". Anything the rules cannot know (the actor, the benefit, each step's observable result) is written as `[NEEDS CLARIFICATION: Qn ...]` and listed under Open questions.
- **clarify**: replaces every marker for each answered question with the answer, and appends a dated Clarifications section with question and answer.
- **plan**: `plan.md` with Approach, Artifacts and handoffs, Tools from the catalogue, Risks, and Quality gates. Tools are rows of the catalogue's `TOOL_SELECTION.md` ranked by BM25 against the spec, each cited by line. Gates are rows of `QUALITY_GATES.md` (the two best matches, plus Engineering and Delivery), each cited by line, plus a Traceability gate. The catalogue is found by `--catalogue`, `SPECFLOW_CATALOGUE`, or by looking upward from the spec; without one, built-in Engineering and Delivery gates are used. Refuses while questions are open (override: `--allow-open`).
- **tasks**: `tasks.md` with numbered tasks `T001...`, each ending in `(traces: ACn.m, ...)`: a setup task, a test-first pair (write the failing check, then implement) per criterion, then gates and the execution report. Refuses while markers remain.
- **analyze**: fails when a criterion has no task, a task traces to nothing or to an unknown criterion, a criterion is not Given/When/Then, a marker is unresolved, the plan names no gate, or the plan or tasks are stale (they record the digest of the spec and plan they were built from).
- **approve**: sets `Status: approved by NAME on DATE` and refreshes the recorded digests.

## What it does not do, compared with Spec Kit

- No model writes the spec. Stories and criteria come from fixed rules and the description's wording, so they are only as good as the description and the answers. Treat the generated text as a draft to edit.
- No agent integration, slash commands, scripts or checklist templates. It does not run the implementation.
- Tool and gate picks are keyword ranking, not judgement. The plan says "Existing stack first"; a person decides.
- `analyze` checks structure and traceability, not whether a criterion is a good one.

## Test

```sh
python test.py                     # catalogue root defaults to two folders up (read only)
python test.py --catalogue <path>
```

The test runs init, specify, clarify, plan, tasks and analyze on the GLB feature above in a temporary folder; checks the refusals while questions are open; checks the plan cites `Three.js with a validated GLB` from `TOOL_SELECTION.md` and names the Delivery, Engineering and Interactive 3D gates; checks every criterion has a task and every task a criterion. Then it breaks the flow five ways (a task with no trace, a criterion with no task, a trace to an unknown criterion, a new open question, a plan with no gates) and checks `analyze` fails each time, approves the spec, and runs a second feature with no actor and no catalogue.

Result on 26 Nov 2026: **29/29 checks passed**. Sample: 3 stories, 6 criteria, 15 tasks; gates Geometry, Interactive 3D, Engineering, Delivery, Traceability. See `out/result.json` and `out/sample/`.
