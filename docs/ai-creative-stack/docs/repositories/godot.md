# Godot Engine

Use for building and exporting complete 2D and 3D games from one editor to desktop, mobile and web targets.

> #42 · Game development · Source E (games) · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/godotengine/godot)
- Verified 2026-11-27 against default branch `master` at [`7c97c297793c`](https://github.com/godotengine/godot/commit/7c97c297793ce4711679491d34693a5719a79ebe).
- GitHub reports archive state **false** and a repository push at `2026-11-26T23:52:18Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Listed in the game-development post (source E, transcript supplied by the user on 2026-11-27).

- [README.md](https://github.com/godotengine/godot/blob/7c97c297793ce4711679491d34693a5719a79ebe/README.md)
- [version.py](https://github.com/godotengine/godot/blob/7c97c297793ce4711679491d34693a5719a79ebe/version.py)
- [register_types.cpp](https://github.com/godotengine/godot/blob/7c97c297793ce4711679491d34693a5719a79ebe/modules/jolt_physics/register_types.cpp)
- [config.py](https://github.com/godotengine/godot/blob/7c97c297793ce4711679491d34693a5719a79ebe/modules/jolt_physics/config.py)
- [physics_server_3d_manager.cpp](https://github.com/godotengine/godot/blob/7c97c297793ce4711679491d34693a5719a79ebe/servers/physics_3d/physics_server_3d_manager.cpp)
- [editor_node.cpp](https://github.com/godotengine/godot/blob/7c97c297793ce4711679491d34693a5719a79ebe/editor/editor_node.cpp)
- [project_dialog.cpp](https://github.com/godotengine/godot/blob/7c97c297793ce4711679491d34693a5719a79ebe/editor/project_manager/project_dialog.cpp)
- [ProjectSettings.xml](https://github.com/godotengine/godot/blob/7c97c297793ce4711679491d34693a5719a79ebe/doc/classes/ProjectSettings.xml)
- [README.md](https://github.com/godotengine/godot/blob/7c97c297793ce4711679491d34693a5719a79ebe/thirdparty/README.md)
- [CHANGELOG.md](https://github.com/godotengine/godot/blob/7c97c297793ce4711679491d34693a5719a79ebe/CHANGELOG.md)
- [CHANGELOG.md](https://github.com/godotengine/godot/blob/4.4-stable/CHANGELOG.md)

## Runtime, hardware and setup

- **Type** game engine. Primary language C++.
- **Platforms** Linux, Windows, macOS, Android, iOS, visionOS, Web.
- **Runtime** Pinned commit is Godot 4.8 release candidate (version.py: major 4, minor 8, status rc). Official binaries from the Godot website; build-from-source requirements are on the docs site and were not read. Otherwise Unverified.
- **Execution** local.
- **Agent paths** Generic coding agent via project files. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Per-project settings live in project.godot. The 3D physics engine is chosen with physics/3d/physics_engine (DEFAULT, GodotPhysics3D, Jolt Physics, Dummy); new projects are written with Jolt Physics.
- **Credentials and services** None for the engine. Console export needs separate licensing (README links godotengine.org/consoles).

| Hardware | Documented value |
| --- | --- |
| GPU | unverified |
| Minimum VRAM | Not documented |
| Recommended VRAM | Not documented |
| System RAM | Not documented |
| Storage | Not documented |
| CPU fallback | not documented |
| Training versus inference | Not documented |
| Notes | README states no GPU or RAM requirements. New projects default the Windows rendering driver to d3d12 (editor_node.cpp initial settings). |

No install command is documented upstream. Follow the pinned documentation.

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | GDScript and C++ (GDExtension) code, Scenes (.tscn/.scn) and resources (.tres/.res), Imported assets such as images, audio and 3D models |
| Output | Exported game builds for Android, iOS, Linux/BSD, macOS, visionOS, Web and Windows (platform/*/export folders) |
| Primary | Game engine |
| Supporting | Physics, 3D rendering, Animation, Level design, Game audio, Prototyping |

Skip when the game must run as a small embeddable web bundle inside an existing JS site; Phaser or Babylon.js fit that better. Consider [bevy](bevy.md), [phaser](phaser.md), [babylonjs](babylonjs.md). Complementary tools include [godot-mcp](godot-mcp.md), [jolt-physics](jolt-physics.md), [pixelorama](pixelorama.md), [blockbench](blockbench.md), [ldtk](ldtk.md), [ink](ink.md), [nakama](nakama.md), [colyseus](colyseus.md), [jsfxr](jsfxr.md), [blender-mcp](blender-mcp.md), [pixelfx](pixelfx.md).

- Changing physics/3d/physics_engine requires a restart; DEFAULT still maps to GodotPhysics3D for projects not created by the editor.

## Craft notes

- At this pinned commit Jolt is built in as a module (modules/jolt_physics, bundled Jolt 5.6.0) and EditorNode::get_initial_settings writes physics/3d/physics_engine = Jolt Physics into every new project.
- ProjectSettings docs say DEFAULT still means GodotPhysics3D and that Jolt is the default for projects created starting in Godot 4.6; older projects keep their engine unless changed.
- Godot's bundled Jolt drops upstream Hair, Compute and Shaders folders, so Jolt's GPU hair simulation is not available through Godot.

## Examples

1. **Independent** Create a 3D platformer prototype with a CharacterBody3D and Jolt-backed RigidBody3D props, then export a Web build.
2. **Combined** Proposed handoff: an agent drives godot-mcp to create scenes and run the project, reading Godot's debug output to fix script errors.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- Running a project executes its scripts and GDExtension native libraries with user privileges; only open trusted projects.
- No telemetry is described in the README. Project manager may check for engine updates (engine_update_label.cpp exists); not verified in detail.

**Software license** MIT.

**Commercial use** MIT allows commercial use with no royalties; README says users' games are theirs. Keep the MIT notice. Bundled third-party code (for example Jolt, MIT) lists its own licenses in thirdparty/README.md.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| version | version.py: 'major = 4', 'minor = 8', 'status = "rc"' |
| jolt_default | editor_node.cpp get_initial_settings: settings["physics/3d/physics_engine"] = PhysicsServer3DManager::JOLT_PHYSICS_NAME; |
| jolt_docs | ProjectSettings.xml: 'Jolt Physics is the default for projects created starting in Godot 4.6.' |
| jolt_introduced | 4.4-stable CHANGELOG.md (linked from pinned CHANGELOG): 'Add Jolt Physics as an alternative 3D physics engine (GH-99895)' |
| jolt_version | thirdparty/README.md: 'Version: 5.6.0 (e77f175595e64cb44218cc9d9d56fc365ad0e36a, 2026)' |
| hardware | README.md: no hardware requirements stated; only 'Official binaries ... on the Godot website'. |
| installation | README.md: 'Official binaries for the Godot editor and the export templates can be found on the Godot website' (no command). |
| license | README.md: 'completely free and open source under the very permissive MIT license' |
| model_license | Not applicable; no model weights. |
| inputs | README.md: 'create 2D and 3D games from a unified interface' |
| outputs | README.md: 'exported with one click to a number of platforms'; platform/*/export folders in tree. |
