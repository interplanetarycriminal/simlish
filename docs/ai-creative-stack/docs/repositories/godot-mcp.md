# Godot MCP

Use for letting an MCP agent launch the Godot editor, run a project in debug mode, read its console output, and create or edit scenes.

> #43 · Game development · Source E (games) · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/Coding-Solo/godot-mcp)
- Verified 2026-11-27 against default branch `main` at [`1209744fad78`](https://github.com/Coding-Solo/godot-mcp/commit/1209744fad78f3998f98c7394fd0f6ef50da5281).
- GitHub reports archive state **false** and a repository push at `2026-04-16T23:37:00Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Listed in the game-development post (source E, transcript supplied by the user on 2026-11-27).

- [README.md](https://github.com/Coding-Solo/godot-mcp/blob/1209744fad78f3998f98c7394fd0f6ef50da5281/README.md)
- [package.json](https://github.com/Coding-Solo/godot-mcp/blob/1209744fad78f3998f98c7394fd0f6ef50da5281/package.json)
- [index.ts](https://github.com/Coding-Solo/godot-mcp/blob/1209744fad78f3998f98c7394fd0f6ef50da5281/src/index.ts)
- [godot_operations.gd](https://github.com/Coding-Solo/godot-mcp/blob/1209744fad78f3998f98c7394fd0f6ef50da5281/src/scripts/godot_operations.gd)

## Runtime, hardware and setup

- **Type** MCP server. Primary language JavaScript.
- **Platforms** Linux, Windows, macOS.
- **Runtime** Node.js >=18.0.0 and npm; a local Godot install (GODOT_PATH or auto-detect). Bundled GDScript uses Godot 4 APIs (FileAccess, DirAccess); UID tools require Godot 4.4+.
- **Execution** local.
- **Agent paths** Claude Code, Cline, Cursor, Any MCP client. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Optional env vars GODOT_PATH (Godot executable) and DEBUG=true. A config option strictPathValidation makes a missing Godot path an error instead of falling back to a default path.
- **Credentials and services** None.

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
claude mcp add godot -- npx @coding-solo/godot-mcp
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Project directory containing project.godot, Scene paths, node types and properties as JSON tool arguments, Texture paths for Sprite2D |
| Output | Saved .tscn scenes and scene variants, MeshLibrary resources for GridMap, Captured stdout/stderr debug output, Project info and Godot version text |
| Primary | Game engine, Prototyping |
| Supporting | Level design, Project intelligence |

Skip if you need live editor control (inspector edits, play-in-editor state); the server spawns separate headless Godot processes rather than talking to a running editor. Consider the existing project toolchain. Complementary tools include [godot](godot.md), [pixelorama](pixelorama.md), [blockbench](blockbench.md), [ldtk](ldtk.md), [blender-mcp](blender-mcp.md).

- Package naming mismatch: README installs '@coding-solo/godot-mcp' but package.json at the pinned SHA is named 'godot-mcp' (v0.1.1).

## Craft notes

- Exposes 14 tools: launch_editor, run_project, get_debug_output, stop_project, get_godot_version, list_projects, get_project_info, create_scene, add_node, load_sprite, export_mesh_library, save_scene, get_uid, update_project_uids.
- Complex edits run one bundled script (godot_operations.gd) via 'godot --headless --path <p> --script', passing operation and JSON params, so no temp scripts are generated per call.
- It cannot read the scene tree of a running game or the editor UI; feedback is limited to process console output.

## Examples

1. **Independent** Ask the agent to create a Node2D scene with a Sprite2D, load a texture, run the project and report errors from get_debug_output.
2. **Combined** Proposed handoff: Pixelorama exports a sprite sheet, then godot-mcp's load_sprite places it into a Sprite2D in a new Godot scene.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- run_project spawns 'godot -d --path <project>', so the agent executes arbitrary project scripts and native extensions.
- Scene tools write and overwrite files inside the project (ResourceSaver.save), and update_project_uids resaves resources.
- Path validation only rejects '..'; absolute paths elsewhere on disk are not blocked by the server.
- Without strictPathValidation it silently falls back to a default Godot path if detection fails.
- No network calls found in src/index.ts; axios is a declared dependency but unused there.

**Software license** MIT.

**Commercial use** MIT allows commercial use with the notice kept.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| tools | src/index.ts tool list: name: 'launch_editor' ... name: 'update_project_uids' (14 entries) |
| godot_version | src/index.ts: 'UIDs are only supported in Godot 4.4 or later.' |
| permissions | src/index.ts: spawn(this.godotPath, ['-d', '--path', args.projectPath]) and ['--headless','--path',...,'--script'] |
| hardware | README.md Requirements: 'Godot Engine installed on your system', 'Node.js (>=18.0.0) and npm' |
| installation | README.md: 'claude mcp add godot -- npx @coding-solo/godot-mcp' |
| license | README.md: 'This project is licensed under the MIT License' |
| model_license | Not applicable; no model weights. |
| inputs | README.md: 'Invalid Project Path: Ensure the path points to a directory containing a project.godot file' |
| outputs | README.md: 'Export 3D scenes as MeshLibrary resources for GridMap', 'Retrieve console output and error messages' |
