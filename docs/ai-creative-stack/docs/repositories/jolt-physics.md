# Jolt Physics

Use for multi-core rigid-body, character, vehicle, ragdoll and soft-body physics in C++ games and VR.

> #48 · Game development · Source E (games) · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/jrouwe/JoltPhysics)
- Verified 2026-11-27 against default branch `master` at [`9e53a3f90228`](https://github.com/jrouwe/JoltPhysics/commit/9e53a3f9022842df8379c0df95ebfe501465287f).
- GitHub reports archive state **false** and a repository push at `2026-11-26T15:27:49Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Listed in the game-development post (source E, transcript supplied by the user on 2026-11-27).

- [README.md](https://github.com/jrouwe/JoltPhysics/blob/9e53a3f9022842df8379c0df95ebfe501465287f/README.md)
- [Core.h](https://github.com/jrouwe/JoltPhysics/blob/9e53a3f9022842df8379c0df95ebfe501465287f/Jolt/Core/Core.h)
- [Architecture.md](https://github.com/jrouwe/JoltPhysics/blob/9e53a3f9022842df8379c0df95ebfe501465287f/Docs/Architecture.md)
- [README.md](https://github.com/jrouwe/JoltPhysics/blob/9e53a3f9022842df8379c0df95ebfe501465287f/Build/README.md)

## Runtime, hardware and setup

- **Type** physics engine. Primary language C++.
- **Platforms** Windows, Linux, macOS, FreeBSD, Android, iOS, Web.
- **Runtime** C++17; Visual Studio 2022+, Clang 16+ or GCC 12+; CMake 3.20+. Only depends on the STL; no RTTI or exceptions. x86/x64 needs SSE2 minimum; ARM64 uses NEON. Library version 5.7.0 at pinned commit.
- **Execution** local.
- **Agent paths** Generic coding agent via project files. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Compile-time defines/CMake options such as CROSS_PLATFORM_DETERMINISTIC, JPH_DOUBLE_PRECISION and JPH_ENABLE_DETERMINISM_LOG.
- **Credentials and services** None. Platform Blue (console) builds need NDA-only PlatformBlue.h.

No install command is documented upstream. Follow the pinned documentation.

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Shapes (sphere, box, capsule, convex hull, mesh, height field, compound, etc.), Constraints, motors, ragdoll skeletons, vehicles via C++ API |
| Output | Simulated body states and contacts, Saved physics state for rollback (SaveState), Debug recordings (.jor) for JoltViewer |
| Primary | Physics |
| Supporting | Game engine, Multiplayer, Animation |

Skip if you need 2D physics or a pure JS engine; Jolt is 3D C++ (JS only through the separate JoltPhysics.js project). Consider [rapier](rapier.md), [matter-js](matter-js.md). Complementary tools include [godot](godot.md), [babylonjs](babylonjs.md), [colyseus](colyseus.md), [nakama](nakama.md).

- Cross-platform determinism needs CROSS_PLATFORM_DETERMINISTIC (about 8% slower) and identical source, defines and API call order.

## Craft notes

- Deterministic by default only for the same binary and same API call order; CROSS_PLATFORM_DETERMINISTIC extends this across compilers, OS and architectures, but broadphase queries, listener callback order and GetActiveBodies order stay non-deterministic.
- Bodies do not auto-wake on creation or neighbour removal, and collision queries can run in parallel with the simulation step, which suits background streaming.
- Godot lists as an integration; Godot's pinned source bundles Jolt 5.6.0 (this repo is 5.7.0). Bindings listed: C, C#, Java/Kotlin, JavaScript, Rust, Python, Zig, Jai, Nim.

## Examples

1. **Independent** Build HelloWorld with CMake, then add a wheeled vehicle and a ragdoll and record a .jor file for JoltViewer.
2. **Combined** Documented integration: Godot 4.4+ ships Jolt as a 3D physics backend, and new Godot 4.6+ projects use it by default.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- Native C++ library; no network or file access beyond what the host app adds.
- None documented.

**Software license** MIT.

**Commercial use** MIT allows commercial use; used in Horizon Forbidden West and Death Stranding 2. Contributors must sign a Contributor Agreement for non-trivial PRs.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| version | Jolt/Core/Core.h: '#define JPH_VERSION_MAJOR 5', '#define JPH_VERSION_MINOR 7' |
| determinism | Docs/Architecture.md: 'turn on the CROSS_PLATFORM_DETERMINISTIC option in CMake. This will make the library approximately 8% slower' |
| bindings | README.md 'Bindings for other languages': C, C#, Java or Kotlin, JavaScript, Rust, Python, Zig, Jai, Nim |
| godot | README.md 'Integrations in other engines': '[Godot](https://github.com/godotengine/godot)' |
| hardware | README.md: 'On x86/x64 the minimal requirements are SSE2.' |
| installation | README.md: 'For build instructions go to the Build section.' (no single command; CMake scripts per platform) |
| license | README.md: 'The project is distributed under the MIT license.' |
| model_license | Not applicable; no model weights. |
| inputs | README.md Features: 'Sphere, Box, Capsule ... Mesh (triangle), Terrain (height field)' |
| outputs | README.md: 'record the output of the physics engine using the DebugRendererRecorder class (a .jor file)' |
