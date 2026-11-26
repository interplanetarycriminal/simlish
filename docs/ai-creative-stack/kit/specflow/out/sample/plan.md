# Implementation plan: Upload a GLB model, preview it in a Three.js viewer, and export a validated copy with a manifest

- Spec: specs/001-upload-glb-model-preview-three/spec.md
- Spec digest: 8e691b8e5e86
- Created: 2026-11-26
- Catalogue: TOOL_SELECTION.md and QUALITY_GATES.md

## Approach

Constitution articles that apply: I. Smallest coherent toolchain; II. Test-first traceability; III. Evidence over claims; IV. Privacy; V. One authority.

1. US1 (Upload a GLB model): build the smallest working path, then prove AC1.1, AC1.2 with automated checks.
2. US2 (Preview it in a Three.js viewer): build the smallest working path, then prove AC2.1, AC2.2 with automated checks.
3. US3 (Export a validated copy with a manifest): build the smallest working path, then prove AC3.1, AC3.2 with automated checks.
4. Run the quality gates below, record evidence, and re-run `specflow analyze`.

## Artifacts and handoffs

| Producer | Consumer | Artifact | Check |
| --- | --- | --- | --- |
| Owner | Implementer | specs/001-upload-glb-model-preview-three/spec.md (approved) | `analyze` passes; no open questions |
| Implementer | Reviewer | Output of US1: Upload a GLB model | AC1.1, AC1.2 |
| Implementer | Reviewer | Output of US2: Preview it in a Three.js viewer | AC2.1, AC2.2 |
| Implementer | Reviewer | Output of US3: Export a validated copy with a manifest | AC3.1, AC3.2 |
| Implementer | Owner | Execution report with gate evidence | Every gate below has a result |

## Tools from the catalogue

- 3D assets and spatial capture / Interactive delivery: Three.js with a validated GLB. Recommended. (TOOL_SELECTION.md line 57)
- Existing stack first: add a listed tool only when the spec shows a gap it closes.

## Risks

- Hardware limits (GPU memory, render time); check HARDWARE.md before installing.
- Data may leave the machine; confirm every destination with the owner.
- Asset scale, materials or size may not survive export; validate the GLB.
- Scope creep beyond the user stories; anything else is out of scope.
- An acceptance criterion that cannot be checked automatically; rewrite it before tasks.

## Quality gates

- [ ] Gate: Geometry (Floor): validate_asset.py Floor checks pass: geometry present, no non-manifold edges, no degenerate faces, consistent normals, no loose vertices. Transforms applied; units in meters. (QUALITY_GATES.md line 29)
- [ ] Gate: Interactive 3D (Floor): Scene loads on target hardware with a poster or static fallback. Controls work outside the canvas. Asset scale and materials match the source. (QUALITY_GATES.md line 26)
- [ ] Gate: Engineering (Floor): Clean rebuild from the lockfile. No console errors on the primary path. Error and empty states exist. (QUALITY_GATES.md line 24)
- [ ] Gate: Delivery (Floor): Every declared artifact opens and matches its format. Rights recorded for fonts, images, audio, weights and code. (QUALITY_GATES.md line 35)
- [ ] Gate: Traceability: `specflow analyze` passes (every criterion has a task, every task traces to a criterion).
