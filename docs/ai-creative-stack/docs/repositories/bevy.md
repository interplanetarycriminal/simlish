# Bevy

Use for code-first, data-oriented (ECS) 2D and 3D games and apps written in Rust.

> #45 · Game development · Source E (games) · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/bevyengine/bevy)
- Verified 2026-11-27 against default branch `main` at [`5c485c424a08`](https://github.com/bevyengine/bevy/commit/5c485c424a0834de2a701c85af364ec72367bb22).
- GitHub reports archive state **false** and a repository push at `2026-11-26T21:13:21Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Listed in the game-development post (source E, transcript supplied by the user on 2026-11-27).

- [README.md](https://github.com/bevyengine/bevy/blob/5c485c424a0834de2a701c85af364ec72367bb22/README.md)
- [Cargo.toml](https://github.com/bevyengine/bevy/blob/5c485c424a0834de2a701c85af364ec72367bb22/Cargo.toml)
- [README.md](https://github.com/bevyengine/bevy/blob/5c485c424a0834de2a701c85af364ec72367bb22/examples/README.md)

## Runtime, hardware and setup

- **Type** game engine. Primary language Rust.
- **Platforms** Linux, Windows, macOS, Android, iOS, Web.
- **Runtime** Rust toolchain; Cargo.toml rust-version = 1.100.0 (MSRV), edition 2024. Pinned main is 0.20.0-dev. Wasm builds need wasm32-unknown-unknown and wasm-bindgen-cli.
- **Execution** local.
- **Agent paths** Generic coding agent via project files. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Features are toggled with Cargo features (docs/cargo_features.md). Apps add plugins, e.g. App::new().add_plugins(DefaultPlugins).run().
- **Credentials and services** None.

| Hardware | Documented value |
| --- | --- |
| GPU | unverified |
| Minimum VRAM | Not documented |
| Recommended VRAM | Not documented |
| System RAM | Not documented |
| Storage | Not documented |
| CPU fallback | not documented |
| Training versus inference | Not documented |
| Notes | README gives no GPU requirements. Linux needs extra system packages (docs/linux_dependencies.md, not read). |

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
git checkout latest
cargo run --example breakout
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Rust code (ECS systems), Assets such as glTF scenes, images, audio |
| Output | Native executables, Android and iOS apps, Wasm builds for the browser |
| Primary | Game engine |
| Supporting | 3D rendering, Animation, Game audio, Prototyping |

Skip if you need a visual editor or API stability; README warns 'Important features are missing' and breaking releases arrive about every 3 months. Consider [godot](godot.md), [babylonjs](babylonjs.md), [phaser](phaser.md). Complementary tools include [rapier](rapier.md), [blockbench](blockbench.md), [ldtk](ldtk.md), [pixelorama](pixelorama.md), [blender-mcp](blender-mcp.md), [ink](ink.md), [nakama](nakama.md).

- Bevy has no built-in physics engine; add a crate such as bevy_rapier2d/bevy_rapier3d.

## Craft notes

- No physics crate exists in crates/ at the pinned commit; the only physics material is an example 'Run physics in a fixed timestep' (examples/movement/physics_in_fixed_timestep.rs).
- MSRV tracks near-latest stable Rust; this commit declares rust-version 1.100.0, so older toolchains will refuse to build.
- The Bevy Remote Protocol examples (client, server, app_under_test, integration_test) let an external tool find and click UI in a running app, useful for agent-driven testing.

## Examples

1. **Independent** Build the breakout example, then extend it with a new power-up system as an ECS plugin.
2. **Combined** Proposed handoff: add bevy_rapier3d (from the rapier repo) for rigid bodies and colliders in a Bevy 0.20 scene.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- bevy_remote (BRP) lets external clients query and edit a running app; only enable it on trusted interfaces.
- None documented.

**Software license** MIT OR Apache-2.0 (dual, at your option).

**Commercial use** Dual MIT/Apache-2.0 allows commercial use. Some crates carry extra BSD-like notices; example assets in the repo have other licenses listed in CREDITS.md and are not shipped in published crates.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| version | Cargo.toml: 'version = "0.20.0-dev"' |
| msrv | Cargo.toml: 'rust-version = "1.100.0"'; README: 'MSRV is generally close to "the latest stable release"' |
| platforms | examples/README.md: 'Platform-Specific Examples' with Android, iOS and Wasm sections |
| physics | crates/ list has no physics crate; examples/README.md: 'Run physics in a fixed timestep' |
| hardware | README.md: no hardware requirements; 'Bevy can be built just fine using default configuration on stable Rust.' |
| installation | README.md: 'git checkout latest' then 'cargo run --example breakout' |
| license | README.md: 'dual-licensed under either: MIT License ... Apache License, Version 2.0 ... at your option.' |
| model_license | Not applicable; no model weights. |
| inputs | README.md: 'Data-oriented architecture using the Entity Component System paradigm' |
| outputs | examples/README.md: 'cargo build --release --example lighting --target wasm32-unknown-unknown' |
