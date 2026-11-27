# Blender MCP

Use for authorized agent-assisted edits in a scoped Blender project.

> #14 · Core 3D authoring and rendering · Sources A and B, also listed in Source F (expressive motion) · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/ahujasid/mcp-for-blender)
- Verified 2026-11-26 against default branch `main` at [`a5a8acf2c6ae`](https://github.com/ahujasid/mcp-for-blender/commit/a5a8acf2c6ae44a73670e0caf34663f16456d645).
- GitHub reports archive state **false** and a repository push at `2026-11-18T10:27:07Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Provisional. Sources A and B were recovered from likely matching mirrored posts; the posts themselves were not readable here. The A/B split follows the order of the seed list (simlish README) and catalogue v1.

- [README.md](https://github.com/ahujasid/mcp-for-blender/blob/a5a8acf2c6ae44a73670e0caf34663f16456d645/README.md)
- [LICENSE](https://github.com/ahujasid/mcp-for-blender/blob/a5a8acf2c6ae44a73670e0caf34663f16456d645/LICENSE)
- [pyproject.toml](https://github.com/ahujasid/mcp-for-blender/blob/a5a8acf2c6ae44a73670e0caf34663f16456d645/pyproject.toml)

## Runtime, hardware and setup

- **Type** MCP server and Blender add-on. Primary language Python.
- **Platforms** Unverified.
- **Runtime** Blender with reviewed add-on and uv/Python
- **Execution** local.
- **Agent paths** Codex, Claude Code. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Install the reviewed Blender add-on and connect to its local endpoint in a disposable scene.
- **Credentials and services** Local operations use no separate API key. Optional services have their own requirements.

| Hardware | Documented value |
| --- | --- |
| GPU | unverified |
| Minimum VRAM | Not documented |
| Recommended VRAM | Not documented |
| System RAM | Not documented |
| Storage | Not documented |
| CPU fallback | not applicable |
| Training versus inference | Not documented |

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
codex mcp add blender -- uvx mcp-for-blender
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Agent operations and Blender scene |
| Output | Modified Blender scenes and assets via Blender export |
| Primary | 3D authoring |
| Supporting | Animation |

Skip when no local Blender runtime or arbitrary script execution cannot be approved. Consider [blender-skills](blender-skills.md), [blockbench](blockbench.md). Complementary tools include [three-js](three-js.md), [sam-3d-objects](sam-3d-objects.md), [stable-fast-3d](stable-fast-3d.md), [meshanything-v2](meshanything-v2.md), [unirig](unirig.md), [dream-textures](dream-textures.md), [comfyui-3d-pack](comfyui-3d-pack.md), [dream-loop](dream-loop.md), [trellis-2](trellis-2.md), [onetake](onetake.md), [lemo-opuscar](lemo-opuscar.md), [effectcraft](effectcraft.md), [comfyui](comfyui.md), [godot](godot.md), [godot-mcp](godot-mcp.md), [bevy](bevy.md), [babylonjs](babylonjs.md).

No native integration with catalogue peers is asserted. Examples using another tool are proposed handoffs.

## Craft notes

- The agent runs Blender Python, edits objects and materials, and checks its own work with the look tool: multi-angle sheets, camera, wireframe, X-ray and animation strips.
- Imports from Poly Haven, Sketchfab and Poly Pizza and generates models through Meshy, Tripo, Hyper3D Rodin and Hunyuan3D. Arbitrary Python execution needs a disposable scene on an approved machine.

## Examples

1. **Independent** Open a disposable scene, create a simple object, and inspect scale and material.
2. **Combined** Export via Blender GLB tooling and load the artifact with Three.js. This is a file handoff.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. Blender 5.2.2 itself was tested (fixtures/blender-glb, scripts/blender/validate_asset.py). The MCP add-on and server were not installed.

## Security, privacy and licensing

- Keep the service local and restrict Blender Python execution and external asset providers.
- No external service in the documented base workflow.

**Software license** MIT.

**Commercial use** Preserve applicable license and notice obligations. Verify the rights to bundled or downloaded assets, services and generated inputs separately.
