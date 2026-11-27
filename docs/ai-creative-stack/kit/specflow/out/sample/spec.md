# Feature spec: Upload a GLB model, preview it in a Three.js viewer, and export a validated copy with a manifest

- ID: 001-upload-glb-model-preview-three
- Status: draft
- Created: 2026-11-26
- Input: "Artists can upload a GLB model, preview it in a Three.js viewer, and export a validated copy with a manifest"

## Summary

Artists can upload a GLB model, preview it in a Three.js viewer, and export a validated copy with a manifest

## User stories

### US1: Upload a GLB model

- Priority: P1
- Story: As one of the artists, I want to upload a GLB model, so that asset reviews happen in the browser without Blender.

#### Acceptance criteria

- AC1.1: Given artists have valid input, When they upload a GLB model, Then the model appears in the asset list with its triangle count within 2 seconds.
- AC1.2: Given the input for this step is missing or invalid, When they upload a GLB model, Then the system stops with a clear error message and leaves existing data unchanged.

### US2: Preview it in a Three.js viewer

- Priority: P2
- Story: As one of the artists, I want to preview it in a Three.js viewer, so that asset reviews happen in the browser without Blender.

#### Acceptance criteria

- AC2.1: Given artists have valid input, When they preview it in a Three.js viewer, Then the viewer renders the model with orbit controls and no console errors.
- AC2.2: Given the input for this step is missing or invalid, When they preview it in a Three.js viewer, Then the system stops with a clear error message and leaves existing data unchanged.

### US3: Export a validated copy with a manifest

- Priority: P3
- Story: As one of the artists, I want to export a validated copy with a manifest, so that asset reviews happen in the browser without Blender.

#### Acceptance criteria

- AC3.1: Given artists have valid input, When they export a validated copy with a manifest, Then a GLB and a manifest.json with size, triangle count and validation results are written to the export folder.
- AC3.2: Given the input for this step is missing or invalid, When they export a validated copy with a manifest, Then the system stops with a clear error message and leaves existing data unchanged.

## Functional requirements

- FR-1: The system must let artists upload a GLB model. (US1)
- FR-2: The system must let artists preview it in a Three.js viewer. (US2)
- FR-3: The system must let artists export a validated copy with a manifest. (US3)

## Edge cases

- Empty input, very large input and repeated runs.
- An interrupted run leaves no half-written output.

## Out of scope

- Anything not named in the user stories above.

## Open questions

- Q1: What outcome makes this feature worth building? -> asset reviews happen in the browser without Blender
- Q2: What observable result shows that "upload a GLB model" worked (format, threshold, where it appears)? -> the model appears in the asset list with its triangle count within 2 seconds
- Q3: What observable result shows that "preview it in a Three.js viewer" worked (format, threshold, where it appears)? -> the viewer renders the model with orbit controls and no console errors
- Q4: What observable result shows that "export a validated copy with a manifest" worked (format, threshold, where it appears)? -> a GLB and a manifest.json with size, triangle count and validation results are written to the export folder

## Clarifications

### Session 2026-11-26

- Q1: What outcome makes this feature worth building? -> asset reviews happen in the browser without Blender
- Q2: What observable result shows that "upload a GLB model" worked (format, threshold, where it appears)? -> the model appears in the asset list with its triangle count within 2 seconds
- Q3: What observable result shows that "preview it in a Three.js viewer" worked (format, threshold, where it appears)? -> the viewer renders the model with orbit controls and no console errors
- Q4: What observable result shows that "export a validated copy with a manifest" worked (format, threshold, where it appears)? -> a GLB and a manifest.json with size, triangle count and validation results are written to the export folder
