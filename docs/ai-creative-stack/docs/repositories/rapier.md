# Rapier

Use for fast 2D or 3D rigid-body, joint and soft-body physics in Rust, JavaScript/WASM, C/C++, Python or Bevy.

> #47 · Game development · Source E (games) · smoke test: **passed**

## Evidence and maintenance

- [Canonical reference](https://github.com/dimforge/rapier)
- Verified 2026-11-27 against default branch `master` at [`475caa3ff464`](https://github.com/dimforge/rapier/commit/475caa3ff4646fd9a796b67d14116256f4962bc7).
- GitHub reports archive state **false** and a repository push at `2026-11-01T21:48:29Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Listed in the game-development post (source E, transcript supplied by the user on 2026-11-27).

- [README.md](https://github.com/dimforge/rapier/blob/475caa3ff4646fd9a796b67d14116256f4962bc7/README.md)
- [Cargo.toml](https://github.com/dimforge/rapier/blob/475caa3ff4646fd9a796b67d14116256f4962bc7/Cargo.toml)
- [Cargo.toml](https://github.com/dimforge/rapier/blob/475caa3ff4646fd9a796b67d14116256f4962bc7/crates/rapier3d/Cargo.toml)
- [README.md](https://github.com/dimforge/rapier/blob/475caa3ff4646fd9a796b67d14116256f4962bc7/bindings/typescript/README.md)
- [README.md](https://github.com/dimforge/rapier/blob/475caa3ff4646fd9a796b67d14116256f4962bc7/bindings/bevy_rapier/README.md)
- [Cargo.toml](https://github.com/dimforge/rapier/blob/475caa3ff4646fd9a796b67d14116256f4962bc7/bindings/bevy_rapier/bevy_rapier3d/Cargo.toml)
- [LICENSE](https://github.com/dimforge/rapier/blob/475caa3ff4646fd9a796b67d14116256f4962bc7/bindings/bevy_rapier/LICENSE)

## Runtime, hardware and setup

- **Type** physics engine. Primary language Rust.
- **Platforms** Linux, Windows, macOS, Web.
- **Runtime** Rust workspace version 0.36.1, rust-version 1.86, edition 2024. JS via npm WASM packages; Python package rapier3d (3D, f32 only); C/C++ bindings in bindings/c.
- **Execution** local.
- **Agent paths** Generic coding agent via project files. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Choose crate by dimension and precision (rapier2d, rapier3d, rapier2d-f64, rapier3d-f64). Cargo features include parallel, simd8, serde-serialize, enhanced-determinism, debug-render and experimental fem.
- **Credentials and services** None.

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
rapier3d = { version = "*", features = ["parallel"] }
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Rigid bodies, colliders, joints set via API, URDF and MJCF robot descriptions (rapier3d-urdf, rapier3d-mjcf), Meshes via rapier3d-meshloader |
| Output | Simulated body poses, contacts and events per step, Serialized world state with serde-serialize |
| Primary | Physics |
| Supporting | Game engine, Multiplayer |

Skip if you need cross-platform lockstep but use the default JS build; README says @dimforge/rapier2d/3d are only locally deterministic, so use the -deterministic packages. Consider [jolt-physics](jolt-physics.md), [matter-js](matter-js.md). Complementary tools include [bevy](bevy.md), [babylonjs](babylonjs.md), [three-js](three-js.md), [react-three-fiber](react-three-fiber.md), [phaser](phaser.md), [colyseus](colyseus.md), [nakama](nakama.md).

- Python bindings cover 3D f32 only; there are no 2D or f64 Python bindings yet.

## Craft notes

- JS packages: @dimforge/rapier2d/3d (main), -simd (needs simd128), -deterministic (cross-platform deterministic, less optimized), each also as -compat with base64-embedded WASM for bundlers.
- Rust determinism is opt-in via the enhanced-determinism feature (simba/libm_force + parry3d/enhanced-determinism); 'parallel' multithreads broad phase, narrow phase and solver via rayon.
- Bevy integration lives in-repo as bevy_rapier2d and bevy_rapier3d (bevy_rapier3d 0.37.0 targets bevy 0.20).

## Examples

1. **Independent** Simulate a 3D stack of boxes with rapier3d and the parallel feature, logging contact events each step.
2. **Combined** Proposed handoff: use @dimforge/rapier3d-compat as the physics layer under a Babylon.js or three-js scene.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**passed**. fixtures/game-dev rapier-determinism: @dimforge/rapier2d-compat 0.21.0, 8 boxes stepped 300 times; two runs are bitwise equal with the same SHA-256 world snapshot and all bodies asleep (same machine only).

## Security, privacy and licensing

- Maintainers state AI coding is used extensively for mjcf-rs, rapier3d-mjcf and the Python bindings, with human review.
- None documented.

**Software license** Apache-2.0.

**Commercial use** Apache-2.0 allows commercial use with notice and patent terms. bindings/bevy_rapier carries its own Apache-2.0 LICENSE.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| crates | README.md: 'These crates are rapier2d, rapier3d, rapier2d-f64, and rapier3d-f64.' |
| js_bindings | bindings/typescript/README.md: '@dimforge/rapier3d-deterministic: ... guarantee of a cross-platform deterministic execution' |
| determinism_feature | crates/rapier3d/Cargo.toml: 'enhanced-determinism = ["simba/libm_force", "parry3d/enhanced-determinism"]' |
| bevy | bevy_rapier3d/Cargo.toml: 'name = "bevy_rapier3d"', 'version = "0.37.0"', 'bevy = { version = "0.20"' |
| hardware | README.md: 'SIMD-batched constraint solving and contact processing are always on' |
| installation | README.md: 'rapier3d = { version = "*", features = ["parallel"] }' |
| license | Cargo.toml: 'license = "Apache-2.0"' |
| model_license | Not applicable; no model weights. |
| inputs | crates/ tree: rapier3d-urdf, rapier3d-mjcf, rapier3d-meshloader |
| outputs | crates/rapier3d/Cargo.toml: 'serde-serialize' feature |
