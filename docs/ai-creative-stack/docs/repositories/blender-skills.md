# Blender Skills

Use for giving a coding agent tested Blender 5.x bpy workflows for modeling, UVs, PBR, baking, rigging, animation, export, rendering and asset QA.

> Supplementary research candidates · Supplementary · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/EL4CTEO/blender-skills)
- Verified 2026-11-26 against default branch `main` at [`1a1cc6c49312`](https://github.com/EL4CTEO/blender-skills/commit/1a1cc6c49312f9f370aae86f52b7b907f29c94f6).
- GitHub reports archive state **false** and a repository push at `2026-11-21T14:35:50Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Not attributable to any source post. Identified during related research.

- [README.md](https://github.com/EL4CTEO/blender-skills/blob/1a1cc6c49312f9f370aae86f52b7b907f29c94f6/README.md)
- [SKILL.md](https://github.com/EL4CTEO/blender-skills/blob/1a1cc6c49312f9f370aae86f52b7b907f29c94f6/skills/blender-core/SKILL.md)
- [run_in_blender.py](https://github.com/EL4CTEO/blender-skills/blob/1a1cc6c49312f9f370aae86f52b7b907f29c94f6/skills/blender-core/scripts/run_in_blender.py)
- [SKILL.md](https://github.com/EL4CTEO/blender-skills/blob/1a1cc6c49312f9f370aae86f52b7b907f29c94f6/skills/blender-texturing/SKILL.md)
- [install.sh](https://github.com/EL4CTEO/blender-skills/blob/1a1cc6c49312f9f370aae86f52b7b907f29c94f6/install/install.sh)
- [plugin.json](https://github.com/EL4CTEO/blender-skills/blob/1a1cc6c49312f9f370aae86f52b7b907f29c94f6/.claude-plugin/plugin.json)
- [LICENSE](https://github.com/EL4CTEO/blender-skills/blob/1a1cc6c49312f9f370aae86f52b7b907f29c94f6/LICENSE)

## Runtime, hardware and setup

- **Type** skill collection. Primary language Python.
- **Platforms** Windows, macOS, Linux.
- **Runtime** Blender 5.2 LTS or newer (verified on 5.3); Python to run run_in_blender.py; optional Blender MCP server for live sessions.
- **Execution** local.
- **Agent paths** Claude Code, Codex, OpenCode, Gemini CLI, GitHub Copilot, Cursor. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Installer symlinks skills into ~/.claude/skills and ~/.agents/skills by default; options --agent, --project DIR, --copy, --skills, --uninstall. Blender is located via BLENDER_EXE, then PATH, then standard install folders.
- **Credentials and services** None.

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
/plugin marketplace add EL4CTEO/blender-skills
/plugin install blender-agent-skills@blender-agent-skills

or:
git clone https://github.com/EL4CTEO/blender-skills
./blender-skills/install/install.sh          # macOS / Linux
.\blender-skills\install\install.ps1         # Windows
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Natural-language asset requests, .blend files, Meshes and texture sets, Mocap/animation actions for retargeting, Video files for VSE editing |
| Output | Modified or new .blend files, Exports: glTF/FBX/USD for Roblox, Unity, Unreal, Godot, web (KTX2 on 5.3), Baked texture maps (normal, AO, curvature, ORM), LODs, Renders and turntables, JSON QA reports and contact-sheet review shots |
| Primary | 3D authoring, 3D orchestration |
| Supporting | Retopology, Texturing, Rigging, Animation, 3D rendering, Video editing |

Skip if you are on Blender 4.x or older; the skills target the 5.2+ API and document 5.x breaking changes. Consider [blender-mcp](blender-mcp.md). Complementary tools include [dream-textures](dream-textures.md), [comfyui-3d-pack](comfyui-3d-pack.md), [unirig](unirig.md), [meshanything-v2](meshanything-v2.md), [stable-fast-3d](stable-fast-3d.md), [trellis-2](trellis-2.md), [gaussian-splatting](gaussian-splatting.md).

The skills drive Blender headless or through an optional Blender MCP server.

- The installer deletes any existing skill folder with the same name (rm -rf) before linking, so same-named local skills are overwritten.

## Craft notes

- 28 skills routed through blender-core; every script exposes run(**kw) -> dict and prints JSON, and 67 headless Blender tests back them.
- Strong on 5.x API drift (action.fcurves to channelbags, scene.compositing_node_group, EEVEE enum rename) that breaks older LLM knowledge; nodes are found by type, not localized name.
- Requires numeric verification before 'done': tris, dimensions, qa_check.py for z-fighting, non-manifold and flipped normals, plus rendered contact sheets.

## Examples

1. **Independent** Make a game-ready crate for Unreal with baked normals and LODs, then run blender-asset-qa before export.
2. **Combined** Proposed handoff: generate a raw mesh with stable-fast-3d, then use blender-retopology-uv and blender-export-pipelines to make it game-ready.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- Skills tell the agent to execute arbitrary bpy Python in Blender, either headless via run_in_blender.py or live via a Blender MCP execute_blender_code tool.
- Core rules forbid read_factory_settings and deleting data the agent did not create in live sessions, and ask for a backup copy before destructive batch edits.
- Runs locally; no network calls are documented by the skills.

**Software license** MIT License.

**Commercial use** MIT allows commercial use, modification and redistribution with the copyright notice.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | No GPU requirement stated; 'Requirements: Blender 5.2 LTS or newer' (README.md) |
| installation | '/plugin marketplace add EL4CTEO/blender-skills' (README.md) |
| license | 'MIT License Copyright (c) 2026 EL4CTEO' (LICENSE) |
| model_license | Not applicable; no models |
| inputs | 'Rig this character with Rigify and export it to Unity with a walk cycle' (README.md) |
| outputs | 'Export: glTF/FBX/USD to Roblox, Unity, Unreal, Godot, web' (skills/blender-core/SKILL.md) |
| supported_agents | 'Claude Code, Codex, OpenCode, Gemini CLI, GitHub Copilot and Cursor' (README.md) |
| blender_access | 'Optional: a Blender MCP server ... Without one, agents run Blender in the background.' (README.md) |
