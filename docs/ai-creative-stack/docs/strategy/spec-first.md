# Spec-first scaffolding

Write what done means before doing anything that is hard to undo.

## The minimum specification

| Field | Example |
| --- | --- |
| Deliverable | A 30-second launch film at 1920×1080, 30 fps, with captions |
| Platform and constraints | Renders on one 24 GB GPU; no paid APIs; existing brand tokens |
| Non-goals | No new logo; no voice-over |
| Ownership | One timeline authority (HyperFrames); one `DESIGN.md` |
| Expected structure | `film/scenes/*.html`, `film/out/master.mp4`, `film/report.md` |
| Test strategy | ffprobe stream checks; frame stills at each beat; caption timing |
| Acceptance conditions | Each written so a person or a script can check it |

[Spec Kit](../repositories/spec-kit.md) or the kit's own [specflow](../../kit/specflow/README.md) can generate and check this structure: specflow refuses to plan while open questions remain, and fails if a criterion has no task. Neither is mandatory; a short `SPEC.md` in the project is enough.

## New project

Set up a minimal source structure, a reproducible dependency file, one smoke test that exercises the riskiest feature, and continuous integration if the project will live on. An empty or always-passing test only manufactures green ticks; it is worse than none.

## Existing project

Extend what is there. Read its instructions and conventions, keep unrelated files unchanged, and never re-scaffold. Distinguish a test that passed locally from continuous integration observed passing remotely.

## Check

- Can each acceptance condition fail? If not, rewrite it.
- Does every planned artifact have exactly one owner?
- Is anything irreversible (publishing, deleting, paying, deploying) marked as needing approval?
