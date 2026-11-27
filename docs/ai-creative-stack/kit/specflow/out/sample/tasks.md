# Tasks: Upload a GLB model, preview it in a Three.js viewer, and export a validated copy with a manifest

- Spec: spec.md (digest 8e691b8e5e86)
- Plan: plan.md (digest 22c33cfa8c08)
- Created: 2026-11-26

Each task names the acceptance criteria it serves. Write the check before the code.

## Setup

- [ ] T001 Create the feature skeleton, fixtures and a test runner that exits nonzero on failure (traces: AC1.1, AC1.2, AC2.1, AC2.2, AC3.1, AC3.2)

## US1: Upload a GLB model

- [ ] T002 Write a failing automated check for AC1.1: then the model appears in the asset list with its triangle count within 2 seconds (traces: AC1.1)
- [ ] T003 Implement "Upload a GLB model" until the AC1.1 check passes (traces: AC1.1)
- [ ] T004 Write a failing automated check for AC1.2: then the system stops with a clear error message and leaves existing data unchanged (traces: AC1.2)
- [ ] T005 Implement "Upload a GLB model" until the AC1.2 check passes (traces: AC1.2)

## US2: Preview it in a Three.js viewer

- [ ] T006 Write a failing automated check for AC2.1: then the viewer renders the model with orbit controls and no console errors (traces: AC2.1)
- [ ] T007 Implement "Preview it in a Three.js viewer" until the AC2.1 check passes (traces: AC2.1)
- [ ] T008 Write a failing automated check for AC2.2: then the system stops with a clear error message and leaves existing data unchanged (traces: AC2.2)
- [ ] T009 Implement "Preview it in a Three.js viewer" until the AC2.2 check passes (traces: AC2.2)

## US3: Export a validated copy with a manifest

- [ ] T010 Write a failing automated check for AC3.1: then a GLB and a manifest.json with size, triangle count and validation results are written to the export folder (traces: AC3.1)
- [ ] T011 Implement "Export a validated copy with a manifest" until the AC3.1 check passes (traces: AC3.1)
- [ ] T012 Write a failing automated check for AC3.2: then the system stops with a clear error message and leaves existing data unchanged (traces: AC3.2)
- [ ] T013 Implement "Export a validated copy with a manifest" until the AC3.2 check passes (traces: AC3.2)

## Gates and report

- [ ] T014 Run the plan's quality gates (Geometry, Interactive 3D, Engineering, Delivery, Traceability) and record evidence (traces: AC1.1, AC1.2, AC2.1, AC2.2, AC3.1, AC3.2)
- [ ] T015 Write the execution report: commands, versions, gate results, open issues (traces: AC1.1, AC1.2, AC2.1, AC2.2, AC3.1, AC3.2)
